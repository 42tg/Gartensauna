import test from 'node:test';import assert from 'node:assert/strict';
import {distanceMm,explosionOffset,validPositions,roofPart} from '../src/geometry.js';
test('model metres become measurement millimetres',()=>{assert.equal(distanceMm([0,0,0],[3,4,0]),5000);assert.equal(distanceMm([1,2,3],[1,2,3.6]),600.0000000000001);});
test('explosion changes translation only, including negative axes',()=>{const p={explosion:[-.8,0,1.4]};assert.deepEqual(explosionOffset(p,0),[-0,0,0]);assert.deepEqual(explosionOffset(p,.5),[-.4,0,.7]);assert.deepEqual(p.explosion,[-.8,0,1.4]);});
test('reject malformed and nonfinite scans',()=>{assert.ok(validPositions(new Float32Array([1,2,3])));for(const p of [[],[1,2],[1,2,NaN],[1,2,Infinity]])assert.equal(validPositions(p),false);});
test('roof visibility includes ceiling but not wall or bench',()=>{assert.ok(roofPart('roof_deck'));assert.ok(roofPart('ceiling_boards'));assert.ok(!roofPart('bench_upper'));});
