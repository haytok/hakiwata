#!/bin/bash
commit_hash_list=(`git log --pretty=%H`);
index=1;
git diff ${commit_hash_list[$index]} --name-only
# git diff ${commit_hash_list[$index]}
# echo ${commit_hash_list[$index]};
echo hoge
