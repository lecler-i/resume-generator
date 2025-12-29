from docxtpl import DocxTemplate, RichText

import json
import logging
import subprocess

logging.basicConfig(level=logging.DEBUG)

def generate_docx(resume, template, output):
    logging.info(f"Loading json file {resume}")
    with open(resume) as f:
        resume_data = json.load(f)

    doc = DocxTemplate(template)

    # Need this usage of richtext to be able to add links for website/mailto
    if resume_data['basics']['website']:
        rt_website = RichText()
        rt_website.add(resume_data['basics']['website'], url_id=doc.build_url_id(resume_data['basics']['website']))
        resume_data['website_link'] = rt_website
    if resume_data['basics']['email']:
        rt_email = RichText()
        rt_email.add(resume_data['basics']['email'], url_id=doc.build_url_id("mailto:" + resume_data['basics']['email']))
        resume_data['email_link'] = rt_email

    doc.render(resume_data)
    doc.save(output)
    return output

def convert_docx_pdf(docxpath):
    logging.info(f"Exporting {docxpath} to pdf")
    subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', docxpath])


def main():
    resume = '/home/ghjkl/ghq/github.com/lecler-i/resume-generator/resumejson/resume-fr.json'
    template = './templates/template-simple.docx'
    output_docx = 'output.docx'
    output_pdf = 'output.pdf'

    convert_docx_pdf(generate_docx(resume, template, output_docx))

if __name__ == "__main__":
    main()
