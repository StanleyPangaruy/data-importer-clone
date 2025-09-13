#!/bin/bash
branch=$(git rev-parse --abbrev-ref HEAD)

if [ "$branch" = "main" ] || \
   [ "$branch" = "staging" ] || \
   [[ "$branch" == mvp* ]] || \
   [[ "$branch" == dev* ]]; then
  echo "ERROR: Direct pushes to the protected '$branch' branch are forbidden." >&2
  echo "Please use a feature branch (feat/*, bug/* or exp/*) and a Pull Request." >&2
  exit 1
fi
