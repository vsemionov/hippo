import os
import shutil
import tempfile


WORK_DIR_NAME = 'hippo_jobs'
OUTPUT_FILENAME = 'output.txt'
OUTPUT_DIR_NAME = 'output'
OUTPUT_SUFFIX = '_output.txt'
RESULTS_SUFFIX = '_results'
RESULTS_FORMAT = 'zip'


def prepare_environment(finput):
    input_filename = os.path.basename(finput.name)
    job_name = os.path.splitext(input_filename)[0]
    work_dir_path = os.path.join(tempfile.gettempdir(), WORK_DIR_NAME)
    job_dir_path = os.path.join(work_dir_path, job_name)
    results_basepath = os.path.join(work_dir_path, job_name) + RESULTS_SUFFIX
    output_path = os.path.join(work_dir_path, job_name) + OUTPUT_SUFFIX
    try:
        os.mkdir(work_dir_path)
    except OSError:
        pass
    return job_dir_path, input_filename, output_path, results_basepath

def create_environment(env, finput):
    job_dir_path, input_filename, _, _ = env
    input_path = os.path.join(job_dir_path, input_filename)
    output_dir_path = os.path.join(job_dir_path, OUTPUT_DIR_NAME)
    os.mkdir(job_dir_path)
    os.mkdir(output_dir_path)
    with finput.open(mode='rb'):
        with open(input_path, mode='wb') as linput:
            shutil.copyfileobj(finput, linput, length=32*1024)

def execute_external(env):
    pass

def save_results(env, perform_save):
    job_dir_path, _, output_path, results_basepath = env
    output_path_orig = os.path.join(job_dir_path, OUTPUT_FILENAME)
    output_dir_path = os.path.join(job_dir_path, OUTPUT_DIR_NAME)
    if os.path.exists(output_dir_path):
        path = shutil.make_archive(results_basepath, RESULTS_FORMAT, job_dir_path)
    else:
        assert os.path.exists(output_path_orig)
        os.rename(output_path_orig, output_path)
        path = output_path
    with open(path, mode='rb') as lresults:
        perform_save(lresults)

def destroy_environment(env):
    job_dir_path, _, _, _ = env
    shutil.rmtree(job_dir_path, ignore_errors=True)

def execute(finput, perform_save):
    env = prepare_environment(finput)
    try:
        create_environment(env, finput)
        execute_external(env)
        save_results(env, perform_save)
    finally:
        destroy_environment(env)
