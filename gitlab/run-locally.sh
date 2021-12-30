#!/bin/bash

if [ -z "$GITLAB_USERNAME" ];
  then read -p "Gitlab Username: " GITLAB_USERNAME;
fi

if [ -z "$GITLAB_PASSWORD" ];
  then read -s -p "Gitlab Password: " GITLAB_PASSWORD;
fi

run_api_unittests()
{
  echo "Running api unit tests..."
  CI_PRE_CLONE_SCRIPT="git config --global lfs.fetchexclude \"backend/bin/models/**/*.hdf5\""

  gitlab-runner exec docker \
    --pre-clone-script "eval \"$CI_PRE_CLONE_SCRIPT\" && git config --global lfs.url https://${GITLAB_USERNAME}:${GITLAB_PASSWORD}@gitlab.com/theseusai/spineai.git/info/lfs" \
    --docker-privileged \
    test:unittest:api
}

run_backend_unittests()
{
  echo "Running backend unit tests..."

  gitlab-runner exec docker \
    --pre-clone-script "git config --global lfs.url https://${GITLAB_USERNAME}:${GITLAB_PASSWORD}@gitlab.com/theseusai/spineai.git/info/lfs" \
    --docker-privileged \
    test:unittest:backend
}

run_backend_docker()
{
  DOCKER_BUILD_DOCKER="docker:19.03.9-dind"

  if [ -z "$DOCKER_ACCESS_TOKEN" ];
   then read -s -p "Docker access token: " DOCKER_ACCESS_TOKEN;
  fi

  gitlab-runner exec docker \
    --pre-clone-script "git config --global lfs.url https://${GITLAB_USERNAME}:${GITLAB_PASSWORD}@gitlab.com/theseusai/spineai.git/info/lfs" \
    --docker-image $DOCKER_BUILD_DOCKER \
    --env DOCKER_ACCESS_TOKEN=$DOCKER_ACCESS_TOKEN \
    --docker-privileged \
    build:docker:backend
}

run_frontend_docker()
{
  DOCKER_BUILD_DOCKER="docker:19.03.9-dind"
  CI_PRE_CLONE_SCRIPT="git config --global lfs.fetchexclude \"backend/bin/models/**/*.hdf5\""

  if [ -z "$DOCKER_ACCESS_TOKEN" ];
   then read -s -p "Docker access token: " DOCKER_ACCESS_TOKEN;
  fi

  gitlab-runner exec docker \
    --pre-clone-script "eval \"$CI_PRE_CLONE_SCRIPT\" && git config --global lfs.url https://${GITLAB_USERNAME}:${GITLAB_PASSWORD}@gitlab.com/theseusai/spineai.git/info/lfs" \
    --docker-image $DOCKER_BUILD_DOCKER \
    --env DOCKER_ACCESS_TOKEN=$DOCKER_ACCESS_TOKEN \
    --docker-privileged \
    build:docker:frontend
}

run_e2e()
{
  E2E_DOCKER="tensorflow/tensorflow:2.2.0-gpu"
  CI_PRE_CLONE_SCRIPT="git config --global lfs.fetchexclude \"backend/testdata/*\""

  if [ -z "$DOCKER_ACCESS_TOKEN" ];
   then read -s -p "Docker access token: " DOCKER_ACCESS_TOKEN;
  fi

  if [ -z "$POSTGRES_PASSWORD" ];
   then read -s -p "PostgreSQL password: " POSTGRES_PASSWORD;
  fi

  if [ -z "$AWS_ACCESS_KEY_ID" ];
   then read -s -p "AWS Access Key ID: " AWS_ACCESS_KEY_ID;
  fi

  if [ -z "$AWS_SECRET_ACCESS_KEY" ];
   then read -s -p "AWS Secret Access Key: " AWS_SECRET_ACCESS_KEY;
  fi

  gitlab-runner exec docker \
    --pre-clone-script "eval \"$CI_PRE_CLONE_SCRIPT\" && git config --global lfs.url https://${GITLAB_USERNAME}:${GITLAB_PASSWORD}@gitlab.com/theseusai/spineai.git/info/lfs" \
    --docker-image $E2E_DOCKER \
    --env DOCKER_ACCESS_TOKEN=$DOCKER_ACCESS_TOKEN \
    --env POSTGRES_PASSWORD="${POSTGRES_PASSWORD}" \
    --env AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
    --env AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
    --docker-privileged \
    verify:e2e
}



echo ""
PS3="Please select a GitLab pipeline to run: "
OPTIONS=("test:unittest:api" "test:unittest:backend" "build:docker:frontend" "build:docker:backend" "verify:e2e" "Quit")

select opt in "${OPTIONS[@]}"
do
  case $opt in
    "test:unittest:api")
      run_api_unittests
      break
      ;;
    "test:unittest:backend")
      run_backend_unittests
      break
      ;;
    "build:docker:frontend")
      run_frontend_docker
      break
      ;;
    "build:docker:backend")
      run_backend_docker
      break
      ;;
    "verify:e2e")
      run_e2e
      break
      ;;
    "Quit")
      break
      ;;
    *) echo "invalid option $REPLY";;
  esac
done

