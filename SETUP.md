# Aliyun ISI Local Setup

This directory is now pre-configured with a local `.env` file.

## Current Local State

- `ALIYUN_NLS_APP_KEY` has been filled.
- `ALIYUN_ACCESS_KEY_ID` has been filled.
- `ALIYUN_ACCESS_KEY_SECRET` has been filled.
- default region is set to `cn-shanghai`.

## What This Means

You now have the minimum local configuration required for an AI tool to generate runnable Aliyun ISI integration code in this folder.

## Recommended Runtime Pattern

- Keep `.env` only on your local machine.
- If a generated app has a frontend, do not expose `ALIYUN_ACCESS_KEY_SECRET` to browser code.
- Use backend-issued Token flow for production web or mobile apps.

## Suggested Next Tasks

- Generate a Node.js backend TTS demo
- Generate a Node.js backend Token endpoint for frontend ASR/TTS
- Generate a Python batch transcription script
