while true; do
    inotifywait -e create,moved_to,close_write templates/ resumejson/
    resume-generator
done
