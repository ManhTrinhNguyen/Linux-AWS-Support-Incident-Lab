# SAMPLE ONLY — LAB-002: Homepage returns HTTP 502

This is a fictional worked example, not a completed incident or evidence of work.

**Environment:** disposable Docker lab. **Impact:** simulated homepage unavailable.
**Customer report:** “The website stopped working after a proxy configuration change.”

## Investigation reasoning
1. Establish which route fails and when the change happened.
2. Inspect container state. A healthy backend weakens the stopped-service hypothesis.
3. Request /health inside the application container. A 200 indicates that listener
   works locally, but does not yet prove proxy-to-app connectivity.
4. Compare Nginx proxy_pass with the application port. A target of 8999 differs from
   the application's 8000 listener.
5. Correlate the proxy error log with the failed request. Look for upstream connection
   errors and the incorrect target port.

## Cause and recovery
The proxy was configured to contact the wrong port. Restore the correct target,
validate Nginx syntax, and reload. Repeat homepage, health, and write requests.
Insert actual outputs only after running the exercise.

## Sample customer response
“We found that the website gateway was connecting to an incorrect application port.
We corrected the configuration and are checking both page loading and saving.
We will confirm resolution after those checks complete.”

## Prevention
Add an end-to-end request check after proxy changes. A syntax-only check cannot
confirm that a configured upstream is reachable.
