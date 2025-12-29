from docxtpl import DocxTemplate, RichText

import argparse
import json
import logging
import subprocess
from pathlib import Path


def generate_docx(resume, template, output):
    logging.info(f"Loading json file {resume}")
    with resume.open() as f:
        resume_data = json.load(f)

    doc = DocxTemplate(template)

    # Need this usage of richtext to be able to add links for website/mailto
    website_link = resume_data['basics'].get('website', None)
    if website_link:
        rt_website = RichText()
        rt_website.add(website_link, url_id=doc.build_url_id(website_link))
        resume_data['website_link'] = rt_website

    email_link = resume_data['basics'].get('email', None)
    if email_link:
        rt_email = RichText()
        rt_email.add(email_link, url_id=doc.build_url_id(f"mailto:{email_link}"))
        resume_data['email_link'] = rt_email

    doc.render(resume_data)
    doc.save(output)
    return output

def convert_docx_pdf(docxpath, output_dir):
    docxpath = Path(docxpath)

    logging.info(f"Exporting {docxpath} to pdf in {output_dir}")
    subprocess.run([
        'soffice',
        '--headless',
        '--convert-to',
        'pdf',
        '--outdir',
        output_dir,
        str(docxpath),
    ], check=True)
    return output_dir / f"{docxpath.stem}.pdf"



