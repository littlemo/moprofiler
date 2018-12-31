var gulp = require('gulp');
var browserSync = require('browser-sync').create();
var reload = browserSync.reload;


gulp.task('default', function () {
    browserSync.init({
        browser: ["google chrome"],
        server: {
            baseDir: "./build/htmlcov"
        }
    });

    gulp.watch('./build/htmlcov/**/*.{html,markdown,md,yml,json,txt,xml}')
        .on('change', reload);
});
