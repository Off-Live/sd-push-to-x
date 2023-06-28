import launch

if not launch.is_installed("boto3"):
    launch.run_pip("install boto3==1.26.161", "requirement for s3")