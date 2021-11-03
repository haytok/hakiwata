#!/bin/bash
commit_hash_list=(`git log --pretty=%H`);
index=1;
file_list=(`git diff ${commit_hash_list[$index]} --name-only`)
echo $file_list
# git diff ${commit_hash_list[$index]}
# echo ${commit_hash_list[$index]};
