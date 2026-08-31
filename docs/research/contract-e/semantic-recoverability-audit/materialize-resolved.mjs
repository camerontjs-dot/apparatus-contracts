#!/usr/bin/env node
import fs from 'node:fs';
import zlib from 'node:zlib';

const src = process.argv[2] ?? 'docs/research/contract-e/semantic-recoverability-audit/RESOLVED-CONTRACT.json.gz.b64';
const out = process.argv[3] ?? 'RESOLVED-CONTRACT.json';
const b64 = fs.readFileSync(src, 'utf8').trim();
const data = zlib.gunzipSync(Buffer.from(b64, 'base64'));
fs.writeFileSync(out, data);
JSON.parse(data.toString('utf8'));
console.log(out);
