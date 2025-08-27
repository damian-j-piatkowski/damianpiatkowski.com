# S3 Sync Guide

This guide documents the strategy for synchronizing local folders with the
S3 bucket `damianpiatkowski-blog`. It explains how the AWS CLI is configured,
how the `sync` command works, and how to control whether files are updated
or only missing ones are downloaded.

## Purpose
- Provides a reliable way to synchronize project assets with S3
- Ensures only missing or changed files are copied
- Supports strict or relaxed timestamp checks depending on workflow
- Keeps local and remote directories aligned without unnecessary transfers

## Key Features
- **AWS CLI–based syncing** via `aws s3 sync`
- **Environment-aware credentials** configured with `aws configure`
- **Efficient transfers**: only new/changed files are copied
- **Options for stricter control**:
  - `--exact-timestamps` ensures precise timestamp alignment
  - `--skip-existing` avoids overwriting local files

---

## Table of Contents
1. [Configuration](#configuration)  
2. [Basic Sync](#basic-sync)  
3. [Skipping Existing Files](#skipping-existing-files)  
4. [Exact Timestamps](#exact-timestamps)  
5. [Upload vs. Download](#upload-vs-download)  

---

## Configuration

AWS CLI must be configured with an access key and secret for the
`blog-uploader` programmatic account.
Running `aws configure` will prompt you step-by-step for each value:

```bash
aws configure
AWS Access Key ID [None]: xxx
AWS Secret Access Key [None]: xxx
Default region name [None]: eu-central-1
Default output format [None]: json
````

Credentials are stored locally in `~/.aws/credentials`.

---

## Basic Sync

To download files from the bucket into a local folder:

```bash
aws s3 sync s3://damianpiatkowski-blog/thumbnails ./thumbnails --exact-timestamps
```

* Copies missing or updated files
* Skips files that already match (by size and timestamp)

---

## Skipping Existing Files

If you only want to fill in missing files (and never overwrite local ones):

```bash
aws s3 sync s3://damianpiatkowski-blog/thumbnails ./thumbnails --skip-existing
```

---

## Exact Timestamps

By default, `sync` ignores sub-second timestamp differences.
With `--exact-timestamps`, files are recopied if even microsecond differences exist.

Useful for:

* Build pipelines requiring identical timestamps
* Avoiding subtle cache mismatches

---

## Upload vs. Download

* **Download (S3 → local):**

  ```bash
  aws s3 sync s3://damianpiatkowski-blog/thumbnails ./thumbnails
  ```

* **Upload (local → S3):**

  ```bash
  aws s3 sync ./thumbnails s3://damianpiatkowski-blog/thumbnails
  ```

Add `--delete` only if you want to remove files on the destination that no longer exist in the source.

---

## Notes

* Always double-check the direction of your sync (`local → s3` vs `s3 → local`)
* Use `--dryrun` to preview which files would be copied or deleted
* Keep credentials restricted to the `blog-uploader` account for security