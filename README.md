# Operating Trossen Mobile AI

Overview of basic Mobile AI operations: teleoperation, data collection, policy training and inference.

Find more information from the official documentation here: https://docs.trossenrobotics.com/trossen_arm/main/index.html.

## Teleoperation

To teleoperate the system with the cameras, run the following command:

**Note:** If you are new or not confident with controlling the system, set `--robot.max_relative_target` to 5 to limit the robot's sensitivity. Use `null` to unrestrict movement.
```bash
uv run lerobot-teleoperate \
--robot.type=mobileai_robot \
--robot.id=mobile_follower \
--robot.left_arm_ip_address=192.168.1.5 \
--robot.right_arm_ip_address=192.168.1.4 \
--robot.max_relative_target=null \
--robot.cameras="{
    cam_high: {type: intelrealsense, serial_number_or_name: "218622275251", width: 640, height: 480, fps: 30},
    cam_left_wrist: {type: intelrealsense, serial_number_or_name: "130322272903", width: 640, height: 480, fps: 30},
    cam_right_wrist: {type: intelrealsense, serial_number_or_name: "218622271135", width: 640, height: 480, fps: 30},
    }" \
--teleop.type=mobileai_leader_teleop \
--teleop.id=mobile_leader \
--teleop.left_arm_ip_address=192.168.1.3 \
--teleop.right_arm_ip_address=192.168.1.2 \
--display_data=true
```
Run the above code with `--display_data=false` to hide camera and joint angle streams.

* Explain arm startup routine & warning about left wrist roll issue


## Data Collection

To record datasets, you need to first query the huggingface (HF) login information by running the following command: **(UPDATE FOR USING LAUNCH SCRIPT)**
```bash
HF_USER=$(uvx hf auth whoami --format quiet)
echo $HF_USER
```
Ensure the above script prints the the HF username. On the Trossen laptop by default, it should be `mrrl-emcnei`.

Record five episodes and upload your dataset to HF:
```bash
uv run lerobot-record \
--robot.type=mobileai_robot \
--robot.id=mobile_follower \
--robot.left_arm_ip_address=192.168.1.5 \
--robot.right_arm_ip_address=192.168.1.4 \
--robot.cameras="{
    cam_high: {type: intelrealsense, serial_number_or_name: "218622275251", width: 640, height: 480, fps: 30},
    cam_left_wrist: {type: intelrealsense, serial_number_or_name: "130322272903", width: 640, height: 480, fps: 30},
    cam_right_wrist: {type: intelrealsense, serial_number_or_name: "218622271135", width: 640, height: 480, fps: 30},
    }" \
--teleop.type=mobileai_leader_teleop \
--teleop.id=mobile_leader \
--teleop.left_arm_ip_address=192.168.1.3 \
--teleop.right_arm_ip_address=192.168.1.2 \
--display_data=true \
--dataset.repo_id=${HF_USER}/mobileai-dataset-name \
--dataset.episode_time_s=60 \
--dataset.reset_time_s=60 \
--dataset.num_episodes=5 \
--dataset.push_to_hub=true \
--dataset.single_task="Briefly define task (e.g. Pick and place the object)"
```
* resume 
* troubleshoot unstable rps with image writer threads
* push to hub for false
* Add relevant tags
* cache storage location. delete if issue

### Visualizing Datasets

#### Online Visualization
Once you record the dataset, you can visualize it online using the HF visualization tool: https://huggingface.co/spaces/lerobot/visualize_dataset.

The dataset ID is formatted as `<hf-username>/<dataset-id>` (e.g. mrrl-emcnei/mobile-test-dataset).

#### Local Visualization
Execute the following script to locally visualize dataset:
```bash
uv run lerobot-dataset-viz \
--repo-id ${HF_USER}/<dataset-id> \
--episode-index 0
```
If you didn’t upload the dataset (i.e., you used `--control.push_to_hub=false`), you can still visualize it locally with:
```bash
uv run lerobot-dataset-viz \
    --repo-id <local_dir_name>/<dataset-id> \
    --mode local \
    --episode-index 0
```
**Note:** The default path for locally stored datasets is `.cache/huggingface/lerobot/`. If you specified a different path during recording, use that path instead.

### Replaying Episodes

Replay the first episode of a specified dataset on your robot:
```bash
uv run lerobot-replay \
--robot.type=mobileai_robot \
--robot.id=mobile_follower \
--robot.left_arm_ip_address=192.168.1.5 \
--robot.right_arm_ip_address=192.168.1.4 \
--dataset.repo_id=${HF_USER}/<dataset-id> \
--dataset.episode=0
```

## Policy Training

```bash
uv run lerobot-train \
--dataset.repo_id=${HF_USER}/mobileai-dataset-name_20260714_152720 \
--policy.type=act \
--output_dir=outputs/train/act_trossen_ai_mobile_test \
--job_name=act_trossen_ai_mobile_test \
--policy.device=cuda \
--policy.repo_id=${HF_USER}/mobileai_my_policy \
--wandb.enable=false
```

## Policy Evaluation