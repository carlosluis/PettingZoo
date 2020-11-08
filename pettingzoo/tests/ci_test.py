import pettingzoo.tests.api_test as api_test
import pettingzoo.tests.bombardment_test as bombardment_test
import pettingzoo.tests.performance_benchmark as performance_benchmark
import pettingzoo.tests.manual_control_test as test_manual_control

import sys
from .all_modules import all_environments, manual_environments
from .all_modules import all_prefixes
from .render_test import render_test
from .error_tests import error_test
from .seed_test import seed_test
from .save_obs_test import test_save_obs
from .max_cycles_test import max_cycles_test
from .parallel_test import parallel_play_test
import subprocess

assert len(sys.argv) == 7, "ci_test expects 5 arguments: env_id, num_cycles, render, manual_control, performance, save_obs"

num_cycles = int(sys.argv[2])
render = sys.argv[3] == 'True'
manual_control = sys.argv[4] == 'True'
performance = sys.argv[5] == 'True'
save_obs = sys.argv[6] == 'True'


env_id = sys.argv[1]


def perform_ci_test(env_id, num_cycles, render, manual_control, performance, save_obs):
    print("running game {}".format(env_id))
    env_module = all_environments[env_id]
    _env = env_module.env()
    error_collected = []
    try:
        api_test.api_test(_env, num_cycles=num_cycles, render=render, verbose_progress=True)
    except Exception as e:
        error_collected.append("API Test: " + str(e))

    if "classic/" not in env_id:
        parallel_play_test(env_module.parallel_env(), num_cycles=num_cycles)

    seed_test(env_module.env, num_cycles)
    max_cycles_test(env_module, env_id)
    # error_test(env_module.env())

    if save_obs:
        test_save_obs(_env)

    if render:
        try:
            render_test(_env)
        except Exception as e:
            error_collected.append("Render Test:" + str(e))

    if manual_control and env_id in manual_environments:
        try:
            manual_control_fn = env_module.manual_control
            test_manual_control.test_manual_control(manual_control_fn)
        except Exception as e:
            error_collected.append("Manual Control: " + str(e))

    if performance:
        _env = env_module.env()
        performance_benchmark.performance_benchmark(_env)

    return error_collected


if env_id in all_prefixes:
    warning_map = {}
    for e in all_environments:
        if e.startswith(env_id):
            warning_map[e] = perform_ci_test(e, num_cycles, render, manual_control, performance, save_obs)
    f = open("test_output.txt", "w")
    for warn in warning_map:
        warn_list = warning_map[warn]
        if len(warn_list) > 0:
            for w in warn_list:
                f.write(warn + ": " + w + "\n")
else:
    print("Environment: '{}' not in the 'all_environments' list".format(env_id))
