#!/bin/bash
docker stop skrizhal_node_0 skrizhal_node_1 skrizhal_node_2 skrizhal_master
docker remove skrizhal_node_0 skrizhal_node_1 skrizhal_node_2 skrizhal_master
# дале sudo требуется для чистки каталогов созданных докером из под root
sudo rm -rf master/pki/private/*
sudo rm -rf master/pki/certs/*
sudo rm -rf data/*
rm -rf __pycache__


