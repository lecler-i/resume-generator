// const fs = require('fs');
// const resumeSchema  = require('resume-schema');
// 
if (process.argv.length < 3) {
  console.error("Missing argument");
  console.error("Usage : npm test [filename]");
  process.exit(1);
}

var fs = require('fs');
var resumeSchema = require('resume-schema');

const resumeObject = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
validate(resumeObject, (report, err) => {
  if (err) {
    console.error(err.message);
  } 
});

var symbols = {
    ok: '\u2713',
    err: '\u2717'
};

//converts the schema's returned path output, to JS object selection notation.
function pathFormatter(path) {
    var jsonPath = path.split('/');
    jsonPath.shift();
    jsonPath = jsonPath.join('.');
    jsonPath = jsonPath.replace('.[', '[');
    return jsonPath;
}

function errorFormatter(errors) {
    errors.errors.forEach(function(error) {
        console.log('    ', symbols.err, pathFormatter(error.path), 'is', error.params.type, ', expected',
            error.params.expected ? error.params.expected : error.params.format);
    });

    console.log('\n  fail  ' + errors.errors.length, '\n');
    console.log('Please fix your resume.json file and try again'); //wording? link to docs

}

function validate(resumeData, callback) {
    console.log('\n  running validation tests on resume.json ... \n');
    resumeSchema.validate(resumeData, function(report, errs) {
        if (errs) {
            // or json parse errors
            var temp = 'Cannot export. There are errors in your resume.json schema format.\n';
            if (resumeData === undefined) {
                temp += 'Try using The JSONLint Validator at: https://jsonlint.com/\n';
                errs.errors[0].params.type = 'unparsable';
                errs.errors[0].params.expected = 'json';
            }
            callback(true, {
                message: temp
            });
            errorFormatter(errs);
            process.exit(1);

        } else {
            console.log('  ' + symbols.ok + ' Passed all validation tests. \n');
            callback(false);
        }
    });
}
