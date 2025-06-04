# PDF Builder
Dynamically generate a PDF from a template, given a list of items, and the input arguments. The script opens the template, and places the data from the items corresponding to the input arguments within the document, and the provides you with a seperate PDF output. The script can be adjusted as needed to various use cases, but this specific version is for my resume (the various sizing, spacing, and other positioning values reflect that), which displays five projects. I use this as a productivity tool to change out the projects based on the role to adapt my resume best to the job I'm applying to.

## Requirements
`pip install reportlab pdfrw pymupdf`

## Usage
`python pdf_builder.py <arg1> <arg2> <arg3> <arg4> <arg5>`  
You can change the variables within the script to fit different uses.

## Example
The below is for when the script is ran with `python pdf_builder.py item1 item3 item5 item7 item9`  
PDF_Template is the test template, the test inputs are in the input directory, and PDF_Output is the output of the script.