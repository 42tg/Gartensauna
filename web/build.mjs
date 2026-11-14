import { build } from 'esbuild';
import {cp,mkdir,rm} from 'node:fs/promises';
await rm('dist',{recursive:true,force:true});await mkdir('dist',{recursive:true});
await build({entryPoints:['src/app.js'],bundle:true,format:'esm',outfile:'dist/app.js',minify:false});
for(const f of ['index.html','style.css','assets'])await cp(f,`dist/${f}`,{recursive:true});
