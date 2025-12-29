from docxtpl import DocxTemplate, RichText

import argparse
import json
import logging
import subprocess
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)

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
        rt_email.add(email_link, url_id=doc.build_url_id(f"mailto:{email_link)")
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


def main():
    parser = argparse.ArgumentParser(description="Generate resume documents from templates and JSON data.")
    class SplitArgs(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            setattr(namespace, self.dest, values.split(','))

    parser.add_argument(
        'resumejsonfile',
        nargs='?',
        help="Path to resume JSON file (positional alternative to --resume-dir/--language).",
    )
    parser.add_argument(
        'templatefile',
        nargs='?',
        help="Path to DOCX template file (positional alternative to --template/--language).",
    )
    parser.add_argument(
        '--resume-dir',
        default='./resumejson',
        help='Directory containing resume JSON files named resume-<lang>.json',
    )
    parser.add_argument(
        '--template-dir',
        default='./templates',
        help='Directory containing template files named <template>-<lang>.docx',
    )
    parser.add_argument(
        '--template',
        default="simple",
        help='Template name (prefix before -<lang> in template file).',
    )
    parser.add_argument(
        '--language',
        default=['en' ,'fr'],
        action=SplitArgs,
        help='Comma-separated language codes to process (default: en,fr).',
    )
    parser.add_argument(
        '--outdir',
        default='./out',
        help='Directory where generated DOCX/PDF and temporary files are written.',
    )

    args = parser.parse_args()

    outdir = Path(args.outdir).expanduser()
    outdir.mkdir(parents=True, exist_ok=True)

    jobs = []

    # Resolve input files and derive template name/language used for output names.
    if args.resumejsonfile or args.templatefile:
        if not args.resumejsonfile or not args.templatefile:
            parser.error('When using positional arguments, provide both resumejsonfile and templatefile.')

        resume_path = Path(args.resumejsonfile).expanduser()
        template_path = Path(args.templatefile).expanduser()

        template_name = args.template

        if not resume_path.is_file():
            parser.error(f"Resume file not found: {resume_path}")
        if not template_path.is_file():
            parser.error(f"Template file not found: {template_path}")

        jobs.append((resume_path, template_path, "manual"))
    else:
        if not args.template:
            parser.error('Either positional files or both --template and --language must be provided.')

        template_name = args.template
        if not args.language:
            parser.error('At least one language must be specified.')

        for language in args.language:
            resume_path = Path(args.resume_dir) / f"resume-{language}.json"
            template_path = Path(args.template_dir) / f"{template_name}-{language}.docx"

            if not template_path.is_file():
                fallback_template = Path(args.template_dir) / f"{template_name}.docx"
                if fallback_template.is_file():
                    logging.info(f"[{language}] Template {template_path} not found; using fallback {fallback_template}")
                    template_path = fallback_template
                else:
                    parser.error(
                        f"Template file not found: {template_path} (also tried fallback {fallback_template})"
                    )

            if not resume_path.is_file():
                parser.error(f"Resume file not found: {resume_path}")

            jobs.append((resume_path, template_path, f"{template_name}-{language}"))

    for resume_path, template_path, output_base_name in jobs:
        logging.info(f"Processing {output_base_name} template={template_path} resume={resume_path}")

        output_docx = outdir / f"{output_base_name}.docx"

        generated_docx = generate_docx(resume_path, template_path, output_docx)
        generated_pdf = convert_docx_pdf(generated_docx, outdir)

        logging.info(f"Generated DOCX: {generated_docx}")
        logging.info(f"Generated PDF:  {generated_pdf}")

if __name__ == "__main__":
    main()
