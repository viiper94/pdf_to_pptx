# PDF to PPTX Converter

Simple python app to convert PDF presentations to PowerPoint.   
*This app was created as a result of having fun with ChatGPT.*

### Some features:
- free and open-source, no need for accounts or subscriptions
- one-file portable app, no need to install, does not require any dependencies
- superfast offline conversion, no need to upload files to the cloud
- converts .pdf file into .pptx file or .jpeg images
- output slides appears as images, so conversion do not affect on fonts and styles 
- can process multiple files in a queue
- supports different page aspect ratio
- can be used as drag-and-drop app or as console tool
- Windows and macOS (arm64, x86_64) compatible


### Usage:
1. Download [latest package](https://github.com/viiper94/pdf_to_pptx/releases/latest)
2. You can start conversion by:
   - open app and select files or drag them into the window
   - drag and dropping .pdf file or files over app icon
   - open console and use command `path/to/exe <pdf_file> [, <pdf_file>]`
3. Wait, while conversion finished
4. PROFIT!


#### macOS startup issue
On macOS, you can get error message `App is damaged and can't be opened....`. 
In this case you should do following: 
1. Open Terminal
2. Type command `xattr -c path/to/app`. It should remove quarantine flag from the app.
3. Run the app, startup may take some time.
4. Enjoy
