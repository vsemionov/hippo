import os
import shutil
import tempfile
import subprocess


WORK_DIR_NAME = 'hippo_jobs'
OUTPUT_FILENAME = 'output.txt'
OUTPUT_DIR_NAME = 'output'
OUTPUT_SUFFIX = '_output.txt'
RESULTS_SUFFIX = '_results.zip'

NPAMP_PATH = '/npamp/npamp/npamp.py'


def prepare_environment(finput):
    input_filename = os.path.basename(finput.name)
    job_name = os.path.splitext(input_filename)[0]
    work_dir_path = os.path.join(tempfile.gettempdir(), WORK_DIR_NAME)
    input_path = os.path.join(work_dir_path, input_filename)
    output_path = os.path.join(work_dir_path, job_name) + OUTPUT_SUFFIX
    output_dir_path = os.path.join(work_dir_path, job_name)
    results_path = os.path.join(work_dir_path, job_name) + RESULTS_SUFFIX
    return work_dir_path, input_path, output_path, output_dir_path, results_path

def create_environment(env, finput):
    work_dir_path, input_path, _, output_dir_path, _ = env
    try:
        os.mkdir(work_dir_path)
    except OSError:
        pass
    os.mkdir(output_dir_path)
    finput.open(mode='rb')
    with finput, open(input_path, mode='wb') as linput:
        shutil.copyfileobj(finput, linput, length=32*1024)

def execute_external(env):
    work_dir_path, input_path, output_path, output_dir_path, _ = env
    with open(output_path, 'wt') as loutput:
        retcode = subprocess.call((NPAMP_PATH, '-o', output_dir_path, input_path), stdout=loutput, stderr=subprocess.STDOUT, cwd=work_dir_path)
    return retcode

def save_results(env, perform_save_output, perform_save_results):
    _, _, output_path, output_dir_path, results_path = env
    if os.path.exists(output_path):
        with open(output_path, mode='rb') as loutput:
            perform_save_output(loutput, content_type='text/plain')
    if len(os.listdir(output_dir_path)):
        basename, extension = os.path.splitext(results_path)
        aformat = extension[1:]
        path = shutil.make_archive(basename, aformat, output_dir_path)
        assert path == results_path
        with open(results_path, mode='rb') as lresults:
            perform_save_results(lresults, content_type='application/octet-stream')

def destroy_environment(env):
    _, input_path, output_path, output_dir_path, results_path = env
    shutil.rmtree(output_dir_path, ignore_errors=True)
    for path in (input_path, output_path, results_path):
        try:
            os.remove(path)
        except Exception:
            pass

def execute(finput, perform_save_output, perform_save_results):
    env = prepare_environment(finput)
    try:
        create_environment(env, finput)
        retcode = execute_external(env)
        save_results(env, perform_save_output, perform_save_results)
        return None if not retcode else "execution error"
    finally:
        destroy_environment(env)
