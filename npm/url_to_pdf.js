var NodePDF = require('nodepdf');

in_url = process.argv[2]
out_pdf = process.argv[3]

var pdf = new NodePDF(in_url, out_pdf, {
    'paperSize': {
      format: 'A4',
      orientation: 'portrait',
      margin: '2cm'
    }
    //'args': '--debug=true'
});

pdf.on('error', function(msg){
    console.error(msg);
});

pdf.on('done', function(pathToFile){
    console.log(pathToFile);
});

// listen for stdout from phantomjs
pdf.on('stdout', function(stdout){
     // handle
});

// listen for stderr from phantomjs
pdf.on('stderr', function(stderr){
    // handle
});

