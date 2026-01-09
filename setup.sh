#!/bin/bash

project_abs_dir=$(cd "$(dirname "$0")"; pwd)
echo project_abs_dir: ${project_abs_dir}
export NO_PROXY="localhost,127.0.0.1"
export CAMEL_MODEL_LOG_ENABLED=true
export CAMEL_LOG_DIR="${project_abs_dir}/CAMEL_LOG_DIR"
export CAMEL_WORKDIR="${project_abs_dir}/CAMEL_WORKDIR"
# export AZURE_OPENAI_API_KEY=""
# export AZURE_OPENAI_BASE_URL=""
# export AZURE_API_VERSION=""