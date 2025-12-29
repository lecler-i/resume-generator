while true; do
    inotifywait -e create,moved_to,close_write templates/template-simple.docx resumejson/resume-fr.json
    resume-generator
    soffice --headless --convert-to pdf ./output.docx
done
