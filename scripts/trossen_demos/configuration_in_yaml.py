from torch import select_copy
import trossen_arm
import sys
import argparse
import time
from datetime import datetime
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator


def print_configurations(driver: trossen_arm.TrossenArmDriver):
    print("EEPROM factory reset flag:", driver.get_factory_reset_flag())
    print("EEPROM IP method:", driver.get_ip_method())
    print("EEPROM manual IP:", driver.get_manual_ip())
    print("EEPROM DNS:", driver.get_dns())
    print("EEPROM gateway:", driver.get_gateway())
    print("EEPROM subnet:", driver.get_subnet())
    print("EEPROM effort corrections:", driver.get_effort_corrections())
    print(
        "EEPROM friction transition velocities:",
        driver.get_friction_transition_velocities()
    )
    print(
        "EEPROM friction constant terms:",
        driver.get_friction_constant_terms()
    )
    print("EEPROM friction coulomb coefs:", driver.get_friction_coulomb_coefs())
    print("EEPROM friction viscous coefs:", driver.get_friction_viscous_coefs())
    print("Modes:", [mode.value for mode in driver.get_modes()])

    end_effector = driver.get_end_effector()
    print("End effector:")
    print("  palm:")
    print("    mass:", end_effector.palm.mass)
    print("    inertia:", end_effector.palm.inertia)
    print("    origin xyz:", end_effector.palm.origin_xyz)
    print("    origin rpy:", end_effector.palm.origin_rpy)
    print("  finger left:")
    print("    mass:", end_effector.finger_left.mass)
    print("    inertia:", end_effector.finger_left.inertia)
    print("    origin xyz:", end_effector.finger_left.origin_xyz)
    print("    origin rpy:", end_effector.finger_left.origin_rpy)
    print("  finger right:")
    print("    mass:", end_effector.finger_right.mass)
    print("    inertia:", end_effector.finger_right.inertia)
    print("    origin xyz:", end_effector.finger_right.origin_xyz)
    print("    origin rpy:", end_effector.finger_right.origin_rpy)
    print("  offset finger left:", end_effector.offset_finger_left)
    print("  offset finger right:", end_effector.offset_finger_right)
    print("  pitch circle radius:", end_effector.pitch_circle_radius)
    print("  t flange tool:", end_effector.t_flange_tool)

    joint_limits = driver.get_joint_limits()
    print("Joint limits:")
    for i, joint_limit in enumerate(joint_limits):
        print(f"  Joint {i}:")
        print("    position min:", joint_limit.position_min)
        print("    position max:", joint_limit.position_max)
        print("    position tolerance:", joint_limit.position_tolerance)
        print("    velocity max:", joint_limit.velocity_max)
        print("    velocity tolerance:", joint_limit.velocity_tolerance)
        print("    effort max:", joint_limit.effort_max)
        print("    effort tolerance:", joint_limit.effort_tolerance)

    motor_parameters = driver.get_motor_parameters()
    print("Motor parameters:")
    for i, motor_param in enumerate(motor_parameters):
        print(f"  Joint {i}:")
        for mode, param in motor_param.items():
            print(f"    Mode {mode.value}:")
            print("      Position loop:")
            print(
                f"        kp: {param.position.kp}, ki: {param.position.ki}, "
                f"kd: {param.position.kd}, imax: {param.position.imax}"
            )
            print("      Velocity loop:")
            print(
                f"        kp: {param.velocity.kp}, ki: {param.velocity.ki}, "
                f"kd: {param.velocity.kd}, imax: {param.velocity.imax}"
            )

    algorithm_parameter = driver.get_algorithm_parameter()
    print("Algorithm parameter:")
    print("  singularity threshold:", algorithm_parameter.singularity_threshold)

def print_config(driver: trossen_arm.TrossenArmDriver):
    print("EEPROM factory reset flag:", driver.get_factory_reset_flag())
    
    joint_characteristics = driver.get_joint_characteristics()
    gripper_characteristics = joint_characteristics[6]
    print(f"--- Gripper Joint Characteristics ---")
    print(f"    effort correction: {gripper_characteristics.effort_correction}")
    print(f"    friction transition velocity: {gripper_characteristics.friction_transition_velocity}")
    print(f"    friction constant term: {gripper_characteristics.friction_constant_term}")
    print(f"    friction coulomb coef: {gripper_characteristics.friction_coulomb_coef}")
    print(f"    friction viscous coef: {gripper_characteristics.friction_viscous_coef}")
    print(f"    position offset: {gripper_characteristics.position_offset}")

    joint_limits = driver.get_joint_limits()
    joint_limit = joint_limits[6] # Gripper joint
    print("--- Gripper Joint Limits ---")
    print("    position min:", joint_limit.position_min)
    print("    position max:", joint_limit.position_max)
    print("    position tolerance:", joint_limit.position_tolerance)
    print("    velocity max:", joint_limit.velocity_max)
    print("    velocity tolerance:", joint_limit.velocity_tolerance)
    print("    effort max:", joint_limit.effort_max)
    print("    effort tolerance:", joint_limit.effort_tolerance)

    end_effector = driver.get_end_effector()
    print("--- End Effector ---")
    print("  offset finger left:", end_effector.offset_finger_left)
    print("  offset finger right:", end_effector.offset_finger_right)

dt = datetime.now().strftime("%Y%m%d_%H%M%S")

parser = argparse.ArgumentParser(prog="Configure in YAML", description="Load or save a single arm configuration to/from a YAML file.")
parser.add_argument("arm", choices=["ll", "rl", "lf", "rf"], help="Specify which arm to configure: ll (left leader), rl (right leader), lf (left follower), rf (right follower).")
parser.add_argument("-l", "--load", action="store", default=False, const=f"{dt}", nargs="?", help="Load the configuration from a YAML file and enter a value to specify the file's base name. The default value if not entered is the current datetime.")
parser.add_argument("-s", "--save", action="store", default=False, const=f"{dt}", nargs="?", help="Save the configuration to a YAML file and enter a value to specify the file's base name. The default value if not entered is the current datetime.")
args = parser.parse_args()

arm_serv_ip = {'left_leader':'192.168.1.3', 'right_leader':'192.168.1.2', 'left_follower':'192.168.1.5', 'right_follower':'192.168.1.4'}
arm_input_map = {'ll': 'left_leader', 'rl': 'right_leader', 'lf': 'left_follower', 'rf': 'right_follower'}
arm = arm_input_map[args.arm]
endeffector = (
    trossen_arm.StandardEndEffector.wxai_v0_follower 
    if arm in ("left_follower", "right_follower") 
    else trossen_arm.StandardEndEffector.wxai_v0_leader
)

config_dir = Path("/home/trossen-ai/mobileai-lerobot/arm_configs")

if __name__=='__main__':
    # Initialize the driver
    driver = trossen_arm.TrossenArmDriver()

    # Configure the driver
    driver.configure(
        trossen_arm.Model.wxai_v0,
        endeffector,
        arm_serv_ip[arm],
        False
    )

    # Print the configurations
    print(f"Arm: {arm}\nOriginal configurations:\n")
    # print("Initial configurations:")
    print_config(driver)

    # Store the configurations in a YAML file
    if args.save:
        save_filename = f"config_{arm}_{args.save}.yaml"
        save_path = config_dir / save_filename
        driver.save_configs_to_file(str(save_path))
        print(f"\nSaved config to {save_filename}.")

    # Load the configurations from the YAML file
    if args.load:
        load_filename = f"config_{arm}_{args.load}.yaml"
        load_path = config_dir / load_filename
        driver.load_configs_from_file(str(load_path))
        print(f"\nLoaded config from {load_filename}.")
        # Print the loaded configurations
        print("Loaded configurations:\n")
        print_config(driver)

    # print("Moving to home positions...")
    # driver.set_all_modes(trossen_arm.Mode.position)

    # sleep_positions = np.array(driver.get_all_positions())
    # sleep_positions[6] = 0.005
    # home_positions = np.zeros(driver.get_num_joints())
    # # home_positions[1] = np.pi/2
    # # home_positions[2] = np.pi/2
    # home_positions[4] = np.pi/2

    # waypoints = np.array([sleep_positions, sleep_positions, home_positions, home_positions, home_positions, home_positions])
    # timepoints = np.array([0, 1, 3, 4, 6, 7])

    # interpolator_position = PchipInterpolator(timepoints, waypoints, axis=0)
    # interpolator_feedforward_velocity = interpolator_position.derivative()
    # interpolator_feedforward_acceleration = interpolator_feedforward_velocity.derivative()

    # log_dict = {
    #     'time': [],
    #     'positions': [],
    #     'velocities': [],
    #     'efforts': [],
    #     'external_efforts': [],
    # }

    # start_time = time.time()
    # end_time = start_time + timepoints[-1]

    # while time.time() < end_time:
    #     loop_start_time = time.time()
    #     current_time = loop_start_time - start_time

    #     positions = interpolator_position(current_time)
    #     feedforward_velocity = interpolator_feedforward_velocity(current_time)
    #     feedforward_acceleration = interpolator_feedforward_acceleration(current_time)

    #     driver.set_all_positions(
    #         positions,
    #         0.0,
    #         False,
    #         feedforward_velocity,
    #         feedforward_acceleration
    #     )

    #     log_dict['time'].append(current_time)
    #     log_dict['positions'].append(driver.get_all_positions())
    #     log_dict['velocities'].append(driver.get_all_velocities())
    #     log_dict['efforts'].append(driver.get_all_efforts())
    #     log_dict['external_efforts'].append(driver.get_all_external_efforts())
