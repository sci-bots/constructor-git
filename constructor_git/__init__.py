import os
import re
import subprocess as sp
import tempfile as tmp

import path_helpers as ph


CRE_DESCRIBE = re.compile(r'^(?P<GIT_DESCRIBE_TAG>[^\-]+)'
                          r'(-(?P<GIT_DESCRIBE_NUMBER>\d+)-g.*)?$')


def render_template_directory(template_root, output_root, context=None,
                              overwrite=False, **kwargs):
    '''
    Generate recipe for latest package version on PyPi.

    Parameters
    ----------
    template_root : str
        Directory of template directory.  Each file in the template directory
        is rendered as a ``jinja2`` template with the specified
        :data:`context`.
    output_root : str
        Output directory path.
    overwrite : bool, optional
        If ``True``, existing files in output directory are overwritten.
    '''
    import jinja2
    import path_helpers as ph

    output_root = ph.path(output_root)
    template_root = ph.path(template_root)

    output_root.makedirs_p()

    for template_file in template_root.files():
        output_path = output_root.joinpath(template_file.name)

        if output_path.isfile() and not overwrite:
            raise IOError('Output file exists {}.  Use `-f` to overwrite.'
                        .format(output_path))

        with template_file.open('r') as template_fhandle:
            try:
                template = jinja2.Template(template_fhandle.read())
            except:
                template_file.copy(output_path)
            else:
                context = context or {}
                context = context.copy()
                context.update(kwargs)
                text = template.render(**context)

                with output_path.open('w') as output:
                    output.write(text)
    return output_root


def build_miniconda_exe(recipe_directory, output_path, **kwargs):
    '''
    Generate Miniconda `exe` installer `constructor`.

    Parameters
    ----------
    recipe_directory : str
        Directory of template directory.  Each file in the template directory
        is rendered as a ``jinja2`` template with the specified
        :data:`context`.
    output_path : str
        If an existing directory is specified, built file is moved to specified
        directory with filename from build.

        Otherwise, built file is renamed to specified output file path.
    **kwargs
        Additional keyword arguments accepted by
        :py:func:`render_recipe_directory`.

    Returns
    -------
    path_helpers.path
        Path of the built file.
    '''
    output_path = ph.path(output_path).realpath()
    recipe_directory = ph.path(recipe_directory).realpath()

    original_dir = os.getcwd()
    build_root = ph.path(tmp.mkdtemp(prefix='miniconda-'))
    try:
        os.chdir(build_root)
        render_template_directory(recipe_directory, build_root, **kwargs)

        # Use `constructor` to build Miniconda installer.
        sp.check_call(['constructor', '--output-dir={}'.format(build_root),
                       build_root])

        # Path to built Miniconda installer.
        exe_path = build_root.files('*.exe')[0]

        if output_path.isdir():
            output_path = output_path.joinpath(exe_path.name)
        exe_path.move(output_path)
    finally:
        os.chdir(original_dir)
        build_root.rmtree()

