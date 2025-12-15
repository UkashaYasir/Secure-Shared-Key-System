# SecureVault: Technical Documentation & Workflow

## 1. System Overview

SecureVault is a web-based implementation of a **Secure Shared-Key System**. It addresses the security risk of a "single point of failure" in key management by splitting encryption keys among multiple parties using **Shamir's Secret Sharing (SSS)**.

### Core Philosophy
- **Zero-Knowledge Principle**: The server never stores the encryption key. It is generated, used, split, and discarded immediately.
- **Distributed Trust**: Access to a file requires collaboration from a $K$ out of $N$ subset of shareholders.

---

## 2. Cryptographic Architecture

The system uses a hybrid approach combining Symmetric Encryption and Secret Sharing.

### 2.1. File Encryption (AES-256-GCM)
When a file is uploaded:
1.  **Key Generation**: A random 256-bit (32-byte) key is generated using `secrets.token_bytes(32)`.
2.  **Encryption**: The file content is encrypted using **AES-GCM** (Galois/Counter Mode).
    -   AES-GCM provides both confidentiality and integrity.
    -   A unique **Nonce (IV)** is generated for every file.
    -   Output: `Ciphertext`, `Auth Tag`, `Nonce`.
3.  **Storage**: The `Ciphertext`, `Auth Tag`, and `Nonce` are stored in the database/storage. The **Key** is NOT stored.

### 2.2. Key Splitting (Shamir's Secret Sharing)
Immediately after encryption, the 32-byte AES key is treated as the "Secret" ($S$).
1.  **Polynomial Generation**: A random polynomial of degree $K-1$ is generated:
    $$f(x) = S + a_1x + a_2x^2 + ... + a_{k-1}x^{k-1}$$
    Where $S$ is the secret key ($f(0)$).
2.  **Share Generation**: $N$ points are evaluated on this curve:
    $Share_i = (i, f(i))$ for $i = 1...N$.
3.  **Share Protection**: Each share is itself encrypted (hashed/wrapped) with a user-provided password before being downloaded to the user's computer.
4.  **Disposal**: The original polynomial and the secret $S$ are wiped from memory.

### 2.3. Key Reconstruction (Lagrange Interpolation)
To recover the key:
1.  Users upload at least $K$ share files.
2.  The system decrypts the shares using the password.
3.  **Interpolation**: Using Lagrange Interpolation, the system reconstructs $f(x)$ using the $K$ points.
4.  **Secret Recovery**: It computes $f(0)$ to recover the original 32-byte AES key.
5.  This reconstructed key is temporarily held in the user's **Session** (server-side, signed cookie) to allow file decryption.

---

## 3. Application Workflow

### Step 1: Initialization
-   The Flask app connects to Supabase.
-   Database tables (`keysets`, `encrypted_files`, `audit_logs`) are ready.

### Step 2: Key Generation / Encryption Flow
1.  **User Action**: Navigates to "Encrypt File", selects a file (e.g., `contract.pdf`), sets $N=5$, $K=3$.
2.  **Processing**:
    -   Server generates AES Key `0xAB...`.
    -   Encrypts `contract.pdf` -> `enc_contract.bin`.
    -   Splits `0xAB...` into 5 JSON shares.
    -   Uploads `enc_contract.bin` to Supabase Storage.
    -   Records metadata in `encrypted_files` table (including file ID and share threshold).
3.  **Result**:
    -   User downloads a ZIP containing 5 JSON share files.
    -   User gets a success message.
    -   Server forgets the key.

### Step 3: Access / Reconstruction Flow
1.  **User Action**: Navigates to "Reconstruct", uploads 3 random share files from the original 5.
2.  **Processing**:
    -   Server verifies shares belong to the same Key Set.
    -   Server executes Lagrange Interpolation.
    -   Server recovers `0xAB...`.
    -   Key is stored in `session['temp_key']`.
3.  **Result**: User is redirected to "Decrypt" page, effectively "logged in" to that specific key set.

### Step 4: Decryption Flow
1.  **User Action**: Selects `contract.pdf` from the list.
2.  **Processing**:
    -   Server retrieves `enc_contract.bin`, `Nonce`, and `Auth Tag` from Supabase.
    -   Server takes `0xAB...` from Session.
    -   Performs AES-GCM Decryption.
3.  **Result**: User downloads the original, unencrypted `contract.pdf`.

---

## 4. Database Schema

### Table: `files` (or `encrypted_files`)
| Column | Type | Purpose |
|p--- | --- | --- |
| `id` | UUID | Unique File ID |
| `key_set_id` | UUID | Links file to a specific set of shares |
| `ciphertext_url` | String | Path to file in Supabase Storage |
| `nonce` | Hex String | AES-GCM Nonce |
| `auth_tag` | Hex String | AES-GCM Auth Tag |
| `original_filename`| String | Name of the original file |

### Table: `audit_logs`
| Column | Type | Purpose |
|p--- | --- | --- |
| `id` | UUID | Log ID |
| `operation_type` | String | e.g., 'FILE_ENCRYPTED', 'KEY_RECONSTRUCTED' |
| `timestamp` | Datetime | Time of event |
| `details` | JSON | Key IDs, File IDs (never sensitive data) |

---

## 5. Security Architecture

1.  **Session Security**: Key reconstruction sessions expire automatically (Flask Session/Cookie management).
2.  **Transmission**: All traffic should be over HTTPS (in production).
3.  **Audit Integrity**: All operations are written to an append-only log in Supabase, providing a trail of who reconstructed what and when.
