import json
import io
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file, session
from securevault.services import key_manager, file_crypto, reconstruction_engine, audit_logger
from securevault.supabase_client import get_supabase
from securevault.models_supabase import SupabaseModels

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/generate-key', methods=['GET', 'POST'])
def generate_key():
    if request.method == 'POST':
        try:
            n_shares = int(request.form['n_shares'])
            threshold = int(request.form['threshold'])
            label = request.form['label']
            
            # For simplicity, we assume one password for all shares in this demo flow,
            # or handle multiple if UI allows.
            password = request.form['password']
            passwords = [password] * n_shares
            
            if threshold > n_shares or threshold < 2:
                flash('Invalid threshold. Must be 1 < K <= N.', 'danger')
                return redirect(url_for('main.generate_key'))

            result = key_manager.generate_and_split_key(n_shares, threshold, passwords)
            
            # Store KeySet in DB
            key_set = SupabaseModels.create_key_set(n_shares, threshold, label)
            
            # Log
            audit_logger.AuditLogger.log('KEY_GENERATION', user_identifier='Guest', details={'key_set_id': key_set['id'], 'label': label})
            
            # Prepare shares for download - simplified
            shares_export = {
                'key_set_id': key_set['id'],
                'shares': result['encrypted_shares']
            }
            
            # Sanitize label for filename
            safe_label = "".join([c for c in label if c.isalnum() or c in (' ', '-', '_')]).strip().replace(' ', '_')
            
            mem = io.BytesIO()
            mem.write(json.dumps(shares_export, indent=2).encode('utf-8'))
            mem.seek(0)
            
            return send_file(
                mem,
                as_attachment=True,
                download_name=f"secure_shares_{safe_label}.json",
                mimetype='application/json'
            )

        except Exception as e:
            flash(f"Error: {str(e)}", 'danger')
    
    return render_template('generate_key.html')

@bp.route('/encrypt-file', methods=['GET', 'POST'])
def encrypt_file():
    if request.method == 'POST':
        file = request.files.get('file')
        key_set_id = request.form.get('key_set_id')
        
        if not file or not key_set_id:
            flash('File and Key Set are required.', 'danger')
            return redirect(url_for('main.encrypt_file'))

        # Check for active reconstruction session to get the key
        # WAIT - the requirement says "Simplify: Generate NEW AES key, encrypt file, THEN split AES key".
        # Let's support the prompt's Flow #3 "Simplified recommended approach".
        # Flow 3: Upload File -> Generate AES -> Encrypt File -> Split AES -> User gets shares.
        
        try:
            n_shares = int(request.form['n_shares'])
            threshold = int(request.form['threshold'])
            password = request.form['password']
            
            file_bytes = file.read()
            
            # 1. Generate AES KEY
            from securevault.services import security_utils
            aes_key = security_utils.generate_random_key(32)
            
            # 2. Encrypt File
            enc_result = file_crypto.encrypt_file(file_bytes, aes_key)
            
            # 3. Split AES Key
            from securevault.services import sss_manager
            shares = sss_manager.SSSManager.split_secret(aes_key, n_shares, threshold)
            
            # 4. Encrypt Shares
            from securevault.services import share_crypto
            encrypted_shares = []
            for i, share in enumerate(shares):
                # Using same password for all shares for MVP
                enc_share = share_crypto.encrypt_share(share, password)
                enc_share['share_index'] = i + 1
                encrypted_shares.append(enc_share)
                
            # 5. Store Metadata
            # Create a "KeySet" record to track this specific file's key strategy
            key_set = SupabaseModels.create_key_set(n_shares, threshold, f"Key for {file.filename}")
            
            # Upload encrypted file to Supabase Storage
            # Note: Supabase Storage limits might apply.
            storage_path = f"encrypted/{key_set['id']}/{file.filename}.enc"
            get_supabase().storage.from_("encrypted-files").upload(
                path=storage_path,
                file=enc_result['ciphertext'],
                file_options={"content-type": "application/octet-stream"}
            )
            
            # Create File record
            SupabaseModels.create_file_record(
                original_filename=file.filename,
                storage_path=storage_path,
                nonce=enc_result['nonce'],
                auth_tag=enc_result['auth_tag'],
                key_set_id=key_set['id']
            )
            
            audit_logger.AuditLogger.log('FILE_ENCRYPTED', user_identifier='Guest', details={'filename': file.filename, 'key_set_id': key_set['id']})
            
            # Return shares download
            shares_export = {
                'key_set_id': key_set['id'],
                'filename': file.filename,
                'shares': encrypted_shares
            }
            
            mem = io.BytesIO()
            mem.write(json.dumps(shares_export, indent=2).encode('utf-8'))
            mem.seek(0)
            
            return send_file(
                mem,
                as_attachment=True,
                download_name=f"secure_shares_{file.filename}.json",
                mimetype='application/json'
            )
            
        except Exception as e:
            flash(f"Error: {str(e)}", 'danger')

    return render_template('encrypt_file.html')

@bp.route('/reconstruct-key', methods=['GET', 'POST'])
def reconstruct_key():
    if request.method == 'POST':
        try:
            # Handle multiple file uploads for shares
            uploaded_files = request.files.getlist('shares')
            password = request.form['password']
            
            if not uploaded_files:
                flash('No share files uploaded.', 'danger')
                return redirect(url_for('main.reconstruct_key'))

            share_data_list = []
            key_set_id = None
            
            for f in uploaded_files:
                data = json.load(f)
                # Handle if user uploaded the big JSON with all shares or individual share JSONs
                # Assuming individual or extraction logic for MVP
                if 'shares' in data:
                    # It's the bulk file
                    share_data_list.extend(data['shares'])
                    key_set_id = data.get('key_set_id')
                else:
                    # Single share ?
                    share_data_list.append(data)
                    # We'd need key_set_id from somewhere
                    
            if not key_set_id:
                # Try to infer or fail
                 flash('Could not determine Key Set ID from shares.', 'danger')
                 return redirect(url_for('main.reconstruct_key'))

            # Passwords list
            passwords = [password] * len(share_data_list)
            
            session_id = reconstruction_engine.ReconstructionEngine.reconstruct_key(
                key_set_id, share_data_list, passwords
            )
            
            session['active_session_id'] = session_id
            session['active_key_set_id'] = key_set_id
            
            flash('Key successfully reconstructed! You can now decrypt files.', 'success')
            return redirect(url_for('main.decrypt_file'))
            
        except Exception as e:
            flash(f"Reconstruction failed: {str(e)}", 'danger')

    return render_template('reconstruct_key.html')

@bp.route('/decrypt-file', methods=['GET', 'POST'])
def decrypt_file():
    # If we have an active session, show files for that key set
    session_id = session.get('active_session_id')
    key_set_id = session.get('active_key_set_id')
    
    files = []
    if key_set_id:
        files = SupabaseModels.list_files_for_keyset(key_set_id)

    if request.method == 'POST':
        file_id = request.form.get('file_id')
        if not session_id:
            flash("No active reconstruction session.", 'warning')
            return redirect(url_for('main.reconstruct_key'))
            
        file_record = SupabaseModels.get_file_record(file_id)
        if not file_record:
            flash("File not found.", 'danger')
            return redirect(url_for('main.decrypt_file'))

        try:
            # 1. Get Key
            aes_key = reconstruction_engine.ReconstructionEngine.get_key_for_session(session_id)
            if not aes_key:
                flash("Session expired.", 'warning')
                return redirect(url_for('main.reconstruct_key'))

            # 2. Download Encrypted File
            resp = get_supabase().storage.from_("encrypted-files").download(file_record['storage_path'])
            ciphertext = resp # Generic bytes from supabase-py download? 
            # Note: supabase-py download returns bytes directly usually
            
            # 3. Decrypt
            plaintext = file_crypto.decrypt_file(
                ciphertext, 
                aes_key, 
                file_record['nonce'], 
                file_record['auth_tag']
            )
            
            audit_logger.AuditLogger.log('FILE_DECRYPTED', user_identifier='Guest', details={'file_id': file_id})
            
            return send_file(
                io.BytesIO(plaintext),
                as_attachment=True,
                download_name=f"decrypted_{file_record['original_filename']}",
                mimetype='application/octet-stream'
            )

        except Exception as e:
            flash(f"Decryption error: {str(e)}", 'danger')

    return render_template('decrypt_file.html', files=files)

@bp.route('/logs')
def logs():
    # Fetch logs
    # Supabase select
    data = get_supabase().table('audit_logs').select('*').order('timestamp', desc=True).limit(50).execute()
    logs = data.data
    return render_template('logs.html', logs=logs)
