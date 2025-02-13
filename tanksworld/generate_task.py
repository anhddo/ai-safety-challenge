import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--logdir', help='the location of saved policys and logs')
parser.add_argument('--exe', help='the absolute path of the tanksworld executable')
parser.add_argument('--teamname1', help='the name for team 1', default='red')
parser.add_argument('--teamname2', help='the name for team 2', default='blue')
parser.add_argument('--reward_weight', type=float, default=1.0)
parser.add_argument('--penalty_weight', type=float, default=1.0)
parser.add_argument('--ff_weight', type=float, help='friendly fire weight', default=0.0)
parser.add_argument('--curriculum_stop', type=float, help='where to stop the penalty weight annealing', default=-1)
parser.add_argument('--policy_lr', type=float, help='actor learning rate', default=3e-4)
parser.add_argument('--value_lr', type=float, help='critic learning rate', default=1e-3)
parser.add_argument('--entropy_coef', type=float, default=0.0)
parser.add_argument('--batch_size', type=int, default=64)
parser.add_argument('--num_epochs', type=int, default=4)
parser.add_argument('--clip_ratio', type=float, help='PPO clipping ratio', default=0.2)
parser.add_argument('--death_penalty', action='store_true', default=False)
parser.add_argument('--friendly_fire', action='store_true', default=True)
parser.add_argument('--kill_bonus', action='store_true', default=False)
parser.add_argument('--eval_mode', action='store_true', default=False)
parser.add_argument('--visual_mode', action='store_true', default=False)
parser.add_argument('--data_mode', action='store_true', default=False)
parser.add_argument('--num_iter', type=int, help='number of training iterations', default=1000)
parser.add_argument('--num_eval_episodes', type=int, help='number of evaluation episodes', default=100)
parser.add_argument('--save_tag', type=str, help='an additional tag on the training folder (optional)', default='')
parser.add_argument('--load_from_checkpoint', action='store_true', help='load training from the last checkpoint', default=False)
parser.add_argument('--freeze_rep', action='store_true', help='freeze the CNN representation', default=False)
parser.add_argument('--eval_logdir', type=str, help='Directory of policy to be evaluated', default='')
parser.add_argument('--multiplayer', action='store_true', default=False)
parser.add_argument('--valuenorm', action='store_true', help='normalize the value function', default=False)
parser.add_argument('--local_std', action='store_true', help='use state dependent standard deviation', default=False)
parser.add_argument('--beta', action='store_true', help='use beta distribution for actor', default=False)
parser.add_argument('--num_rollout_threads', type=int, help='number of asynchronous environments', default=1)
parser.add_argument('--n_env_seeds', type=int, help='number of different env seeds to train on', default=1)
parser.add_argument('--n_policy_seeds', type=int, help='number of different policy seeds to train on', default=1)
parser.add_argument('--cnn_path', type=str, help='path to load CNN model', default='./models/frozen-cnn-0.8/4000000.pth')
parser.add_argument('--independent', action='store_true', help='use independent training', default=False)
parser.add_argument('--coppo', action='store_true', help='use coordinated PPO', default=False)
parser.add_argument('--single_agent', action='store_true', help='train single agent', default=False)
parser.add_argument('--centralized', action='store_true', help='use centralized training', default=False)
parser.add_argument('--centralized_critic', action='store_true', help='use centralized critic', default=False)
parser.add_argument('--bonus', action='store_true', help='use exploration bonus', default=False)
parser.add_argument('--rnd', action='store_true', help='use rnd', default=False)
parser.add_argument('--noisy', action='store_true', help='use noisy parameters', default=False)
parser.add_argument('--heuristic', type=str, help='use heuristics', default='')
parser.add_argument('--init_log_std', type=float, help='init value of logstd of actor', default=-0.5)
parser.add_argument('--selfplay', action='store_true', help='use selfplay', default=False)
parser.add_argument('--n_eval_seeds', type=int, help='how many evaluation environments', default=10)

parser.add_argument('--cuda_idx', type=int, default=0)
parser.add_argument('--appendix', type=str, default='')

config = vars(parser.parse_args())

cuda_idx = config['cuda_idx']

command = []
for arg_name in config:
    if arg_name == 'cuda_idx': continue
    if arg_name == 'appendix': continue
    arg_value = config[arg_name]
    if isinstance(arg_value, bool):
        if arg_value:
            command += ['--{}'.format(arg_name)]
    else:
        if arg_value != '':
            command += ['--{}'.format(arg_name)]
            command += ['{}'.format(arg_value)]

for seed_idx in range(config['n_policy_seeds']):
    command_to_run = 'CUDA_VISIBLE_DEVICES={} python trainer_new.py '.format(cuda_idx)
    command_to_run += ' '.join(command)
    command_to_run += ' --seed_idx {}'.format(seed_idx)

    with open('./tasks/task{}_cuda{}.sh'.format(seed_idx, cuda_idx), 'w+') as f:
        f.write('TMUX='' tmux new-session -s task{}_cuda{}_{} '.format(seed_idx, cuda_idx, config['appendix']))
        f.write('\'source ~/anaconda3/etc/profile.d/conda.sh\n')
        f.write('conda activate tanksworld\n')
        f.write(command_to_run)
        f.write('\'')