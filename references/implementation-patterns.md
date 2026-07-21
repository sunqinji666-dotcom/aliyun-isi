# Implementation Patterns

Use these patterns to keep generated integrations secure and reusable.

## Pattern 1: Backend Issues Token

Use for web, mobile, mini-program, or desktop clients.

Flow:

1. Client calls your backend.
2. Backend uses AccessKey credentials to talk to Alibaba Cloud auth flow.
3. Backend returns a short-lived Token and any non-secret metadata the client needs.
4. Client calls the ISI SDK or gateway with `Token + AppKey`.

Why this is the default:

- Secrets stay on the server.
- Token rotation is controllable.
- Frontend delivery is simpler.

## Pattern 2: Backend Speech Proxy

Use when:

- the client should never see Aliyun-specific details
- you want request logging, rate limiting, or provider abstraction
- file formats need server-side normalization

Deliverables:

- upload endpoint
- format validation
- conversion or normalization step if needed
- provider call
- normalized response payload

## Pattern 3: Batch Job

Use for:

- recording-file transcription pipelines
- long-text synthesis jobs
- asynchronous content generation

Deliverables:

- job runner or queue consumer
- storage path conventions
- retry and timeout handling
- result callback or polling strategy

## Default Env Names

Use these variable names unless the repository already has a convention:

```env
ALIYUN_ACCESS_KEY_ID=
ALIYUN_ACCESS_KEY_SECRET=
ALIYUN_NLS_APP_KEY=
ALIYUN_REGION=cn-shanghai
ALIYUN_NLS_GATEWAY=
```

## Minimum Verification Checklist

After generating code, verify:

1. Service is activated in the target account.
2. `AppKey` is from the intended ISI project.
3. Token is fresh.
4. Audio format matches the selected API.
5. Secrets are absent from frontend bundles and logs.
6. The sample request succeeds with a known-good input.
