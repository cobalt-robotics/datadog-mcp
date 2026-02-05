#!/bin/bash

uv sync

uv build

uv tool install . --force
