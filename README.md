# SecureVault: Shared-Key Protection System

**SecureVault** is an enterprise-grade secure file storage application that combines **AES-256 Encryption** with **Shamir's Secret Sharing (SSS)**. It ensures that no single person holds the complete key to decrypt sensitive files, distributing trust among multiple stakeholders.

Built with a premium Glassmorphism UI, Flask backend, and Supabase cloud storage.

---

## 🚀 Features

-   **Shamir's Secret Sharing**: Split encryption keys into $N$ shares, requiring a threshold of $K$ shares to reconstruct.
-   **AES-256 File Encryption**: Military-grade encryption for all uploaded files.
-   **No Key Storage**: The decryption key is *never* stored in the database. It exists only ephemerally during creation and reconstruction.
-   **Secure Vault (Supabase)**: Encrypted files and audit logs are stored securely in the cloud.
-   **Audit Logging**: Every operation (Key Generation, Encryption, Reconstruction) is logged with tamper-evident records.
-   **Premium UI**: Modern, responsive interface with animated gradients and glassmorphism effects.

## 🛠️ Technology Stack

-   **Backend**: Python, Flask
-   **Cryptography**: `cryptography` (AES-GCM), `secrets` (CSPRNG)
-   **Database & Storage**: Supabase (PostgreSQL + S3 Storage)
-   **Frontend**: Bootstrap 5.3, FontAwesome, Custom CSS (Glassmorphism)

## 📋 Prerequisites

-   Python 3.10+
-   A [Supabase](https://supabase.com) Project (URL and Anon Key)

## ⚡ Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/yourusername/securevault.git
    cd securevault
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration**
    Copy the example environment file:
    ```bash
    cp .env.example .env
    ```
    Edit `.env` and add your Supabase credentials:
    ```ini
    SUPABASE_URL=your_supabase_project_url
    SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
    SECRET_KEY=your_flask_secret_key
    ```

## 🏃‍♂️ Usage

1.  **Start the Application**
    ```bash
    python app.py
    ```
2.  **Navigate to** `http://localhost:5000`

### Core Workflow
1.  **Generate Key**: Create a new Key ID and download the generic shares (optional step for demo).
2.  **Encrypt File**: Upload a file. The system generates a *random* AES key, encrypts the file, splits the key into $N$ shares (downloaded as JSON), and uploads the encrypted file to Supabase.
3.  **Reconstruct**: When you need to decrypt, upload $K$ of the share files. The system reconstructs the session key in memory.
4.  **Decrypt**: Select the file to decrypt using the active reconstructed session.

## 🧪 Testing

Run the included unit test suite to verify cryptographic correctness:
```bash
python -m unittest discover tests
```

---

*© 2025 SecureVault Team*
