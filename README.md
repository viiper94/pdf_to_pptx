# PDF to PPTX Converter

Simple python app to convert PDF presentations to PowerPoint.  

![Screenshot 2025-01-19 130047 (1)](https://github.com/user-attachments/assets/9142eb57-fd67-4905-90cd-50a6c907899e)

### Key Features:
- **Free and Open-Source**: No accounts or subscriptions required.
- **Portable and Easy to Use**: A single executable file with no installation or dependencies needed.
- **Fast Offline Conversion**: No need to upload files to the cloud.
- **Flexible Output Options**: Converts PDFs to PowerPoint (.pptx) or PNG images.
- **Preserves Fonts and Styles**: Output slides are saved as images, ensuring fonts and styles remain unchanged.
- **Batch Processing**: Handles multiple files in a queue.
- **Supports Various Page Ratios**: Compatible with different aspect ratios.
- **Improved Performance**: Uncompressed PDFs are automatically compressed, enhancing output efficiency and performance.
- **Dual Functionality**: Use as a drag-and-drop app or a command-line tool.
- **Cross-Platform**: Works on both Windows and macOS (arm64, x86_64).


### Usage:
1. Download the [latest package](https://github.com/viiper94/pdf_to_pptx/releases/latest)
2. You can start conversion by:
   - Open the app and select files or drag them into the window.
   - Drag and drop PDF files onto the app icon.
   - Use the command line: `path/to/exe <pdf_file> [, <pdf_file>]`
3. Wait for completion
4. PROFIT!


### macOS startup issue
On macOS, you can get error message `App is damaged and can't be opened....`. 
In this case you should do following: 
1. Open Terminal
2. Run the command `xattr -c path/to/app`. It should remove quarantine flag from the app.
3. Run the app, startup may take a while.
4. Enjoy
