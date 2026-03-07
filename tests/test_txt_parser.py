import unittest
import os
import tempfile
from sdk.parsers.txt_parser import extract_txt_content

class TestTxtParser(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.gettempdir()

    def create_temp_file(self, content, encoding='utf-8', suffix='.txt'):
        fd, path = tempfile.mkstemp(suffix=suffix, dir=self.temp_dir)
        if isinstance(content, str):
            with os.fdopen(fd, 'w', encoding=encoding) as f:
                f.write(content)
        else:
            with os.fdopen(fd, 'wb') as f:
                f.write(content)
        return path

    def test_normal_file(self):
        path = self.create_temp_file("Hello World")
        result = extract_txt_content(path)
        self.assertEqual(result, "Hello World")
        os.remove(path)

    def test_empty_file(self):
        path = self.create_temp_file("")
        result = extract_txt_content(path)
        self.assertIn("[Empty File]", result)
        os.remove(path)

    def test_large_file_truncation(self):
        large_content = "A" * 100
        path = self.create_temp_file(large_content)
        # Test with a very small max_chars to force truncation
        result = extract_txt_content(path, max_chars=10)
        self.assertTrue(result.startswith("AAAAAAAAAA"))
        self.assertIn("[NOTE: Content truncated", result)
        os.remove(path)

    def test_encoding_latin1(self):
        # Text with latin-1 specific chars
        content = "Héllö Lätïn"
        path = self.create_temp_file(content.encode('latin-1'), encoding=None)
        result = extract_txt_content(path)
        # Should fallback to latin-1 and read correctly
        self.assertIn("Héllö Lätïn", result)
        os.remove(path)

    def test_binary_file_safety(self):
        # Simulating a binary file that might be renamed to .txt
        binary_content = b'\xff\xfe\xfd\x00\x01\x02'
        path = self.create_temp_file(binary_content, encoding=None)
        result = extract_txt_content(path)
        # Should not crash, should return something (even if mangled) or error message
        self.assertIsInstance(result, str)
        os.remove(path)

    def test_file_not_found(self):
        result = extract_txt_content("non_existent_file.txt")
        self.assertIn("[Error] File not found", result)

if __name__ == '__main__':
    unittest.main()
