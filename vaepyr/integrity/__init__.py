import hashlib
import os

class GoldenState:
    @staticmethod
    def generate_merkle_root(directory):
        """
        Recursively hash all files in the directory to create a single master hash (Merkle Root).
        Logic:
        1. Collect all file paths (sorted).
        2. Hash each file.
        3. If only 1 file exists, the master hash IS the file hash (optimization for single-page sites).
        4. If multiple files, hash the concatenation of all file hashes.
        """
        file_hashes = []
        files_found = []
        for root, dirs, files in os.walk(directory):
            for file in sorted(files):
                filepath = os.path.join(root, file)
                files_found.append(filepath)
                with open(filepath, 'rb') as f:
                    file_content = f.read()
                    file_hashes.append(hashlib.sha256(file_content).hexdigest())

        if not file_hashes:
            raise ValueError("Directory is empty")

        if len(file_hashes) == 1:
            return file_hashes[0]

        master_string = "".join(file_hashes)
        return hashlib.sha256(master_string.encode('utf-8')).hexdigest()

    @staticmethod
    def verify_stream(content, expected_hash):
        """
        Verify incoming data content against the expected hash.
        """
        calculated_hash = hashlib.sha256(content).hexdigest()
        if calculated_hash != expected_hash:
            raise SecurityException(f"Integrity Check Failed! Expected {expected_hash}, got {calculated_hash}")
        return True

class SecurityException(Exception):
    pass

class SignalIntegrity:
    """
    Handles the embedding and verification of signals in the data stream.
    """

    SIGNAL_INDICES = [7, 37, 60]

    @staticmethod
    def embed_signals(data_str, node_checksum):
        """
        Embeds the node_checksum character into the data_str at indices 7, 37, 60.
        """
        target_len = max(SignalIntegrity.SIGNAL_INDICES) + 1
        if len(data_str) < target_len:
            data_str = data_str.ljust(target_len, ' ')

        data_list = list(data_str)
        signal_char = node_checksum[0] if node_checksum else '0'

        for idx in SignalIntegrity.SIGNAL_INDICES:
            data_list[idx] = signal_char

        return "".join(data_list)

    @staticmethod
    def verify_signals(data_str, expected_checksum_char):
        """
        Verifies signals and Returns the CLEANED data string (restoring spaces).
        """
        if len(data_str) <= max(SignalIntegrity.SIGNAL_INDICES):
            return False, None

        for idx in SignalIntegrity.SIGNAL_INDICES:
            if data_str[idx] != expected_checksum_char:
                return False, None

        # Restore spaces so JSON parser works
        data_list = list(data_str)
        for idx in SignalIntegrity.SIGNAL_INDICES:
            data_list[idx] = ' '

        return True, "".join(data_list)
