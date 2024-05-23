/**
 * Gulpfile for minifying CSS files and watching for changes.
 *
 * This Gulp configuration performs the following tasks:
 * - Minifies 'base.css' and 'index.css' separately.
 * - Watches for changes in 'base.css' and 'index.css' and re-minifies them as needed.
 * - Uses 'gulp-changed' to only process modified files, improving performance.
 *
 * Tasks:
 * - minifyBaseCss: Minifies 'base.css'.
 * - minifyIndexCss: Minifies 'index.css'.
 * - watch: Watches for changes in 'base.css' and 'index.css'.
 * - default: Runs 'minifyBaseCss', 'minifyIndexCss', and 'watch' in parallel.
 */

const gulp = require('gulp');
const cssnano = require('gulp-cssnano');
const changed = require('gulp-changed');
const path = require('path');

const cssSrc = path.join(__dirname, '../static/css');
const cssDest = path.join(__dirname, '../static/dist/css');

const baseCss = path.join(cssSrc, 'base.css');
const indexCss = path.join(cssSrc, 'index.css');

/**
 * Task to minify 'base.css'.
 * Only processes the file if it has changed.
 */
function minifyBaseCss() {
    return gulp.src(baseCss)
        .pipe(changed(cssDest, { extension: '.min.css' }))
        .pipe(cssnano())
        .pipe(gulp.dest(cssDest));
}

/**
 * Task to minify 'index.css'.
 * Only processes the file if it has changed.
 */
function minifyIndexCss() {
    return gulp.src(indexCss)
        .pipe(changed(cssDest, { extension: '.min.css' }))
        .pipe(cssnano())
        .pipe(gulp.dest(cssDest));
}

/**
 * Watch task to monitor changes in 'base.css' and 'index.css'.
 * Runs the appropriate minification task when changes are detected.
 */
function watchFiles() {
    gulp.watch(baseCss, minifyBaseCss);
    gulp.watch(indexCss, minifyIndexCss);
}

gulp.task('minifyBaseCss', minifyBaseCss);
gulp.task('minifyIndexCss', minifyIndexCss);
gulp.task('watch', watchFiles);

/**
 * Default task that runs 'minifyBaseCss', 'minifyIndexCss', and 'watch' in parallel.
 */
gulp.task('default', gulp.parallel('minifyBaseCss', 'minifyIndexCss', 'watch'));
