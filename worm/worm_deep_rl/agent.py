import tensorflow as tf
import reverb

from tf_agents.policies import py_tf_eager_policy
from tf_agents.agents.dqn import dqn_agent
from tf_agents.drivers import py_driver
from tf_agents.specs import tensor_spec
from tf_agents.utils import common

from env import Env
from helper import Helper

num_iterations = 20000  # @param {type:"integer"}

initial_collect_steps = 100  # @param {type:"integer"}
collect_steps_per_iteration = 1  # @param {type:"integer"}
replay_buffer_max_length = 100000  # @param {type:"integer"}

batch_size = 64  # @param {type:"integer"}
learning_rate = 1e-3  # @param {type:"number"}
log_interval = 200  # @param {type:"integer"}

num_eval_episodes = 10  # @param {type:"integer"}
eval_interval = 1000  # @param {type:"integer"}


class Agent:
    def __init__(self):
        optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)

        train_step_counter = tf.Variable(0)

        self.train_env = Env()

        self.agent = dqn_agent.DqnAgent(
            self.train_env.time_step_spec(),
            self.train_env.action_spec(),
            q_network=Helper.model(),
            optimizer=optimizer,
            td_errors_loss_fn=common.element_wise_squared_loss,
            train_step_counter=train_step_counter)

        self.agent.initialize()

        # Policy
        eval_policy = self.agent.policy
        collect_policy = self.agent.collect_policy

    # @test {"skip": true}
    def compute_avg_return(self, num_episodes=10):

        total_return = 0.0
        for _ in range(num_episodes):

            time_step = self.train_env.reset()
            episode_return = 0.0

            while not time_step.is_last():
                action_step = self.agent.policy.action(time_step)
                time_step = self.train_env.step(action_step.action)
                episode_return += time_step.reward
            total_return += episode_return

        avg_return = total_return / num_episodes
        return avg_return.numpy()[0]

    def replay_buffer(self):
        table_name = 'uniform_table'
        replay_buffer_signature = tensor_spec.from_spec(
            self.agent.collect_data_spec)
        replay_buffer_signature = tensor_spec.add_outer_dim(
            replay_buffer_signature)

        table = reverb.Table(
            table_name,
            max_size=replay_buffer_max_length,
            sampler=reverb.selectors.Uniform(),
            remover=reverb.selectors.Fifo(),
            rate_limiter=reverb.rate_limiters.MinSize(1),
            signature=replay_buffer_signature)

        reverb_server = reverb.Server([table])

        replay_buffer = self.reverb_replay_buffer.ReverbReplayBuffer(
            self.agent.collect_data_spec,
            table_name=table_name,
            sequence_length=2,
            local_server=reverb_server)

        self.rb_observer = self.reverb_utils.ReverbAddTrajectoryObserver(
            replay_buffer.py_client,
            table_name,
            sequence_length=2)

    def train(self):
        self.agent.train_step_counter.assign(0)

        avg_return = self.compute_avg_return(num_eval_episodes)
        returns = [avg_return]

        time_step = self.train_env.reset()

        collect_driver = py_driver.PyDriver(
            self.train_env,
            py_tf_eager_policy.PyTFEagerPolicy(
                self.agent.collect_policy, use_tf_function=True),
            [rb_observer],
            max_steps=collect_steps_per_iteration)

