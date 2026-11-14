export function distanceMm(a,b){return Math.hypot(...a.map((v,i)=>v-b[i]))*1000;}
export function explosionOffset(part,amount){return part.explosion.map(v=>v*amount);}
export function validPositions(array){return array.length>0&&array.length%3===0&&array.every(Number.isFinite);}
export const roofPart=name=>/^(roof_|ceiling_)/.test(name);
