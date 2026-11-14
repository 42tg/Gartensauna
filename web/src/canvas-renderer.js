// CPU fallback for browsers without WebGL. Uses the same CAD triangles and
// real scan points; caps only displayed scan points, never synthesizes geometry.
import * as THREE from 'three';
export class CanvasRenderer {
 constructor(){this.domElement=document.createElement('canvas');this.context=this.domElement.getContext('2d');this.isFallback=true;this.last='';}
 setPixelRatio(){} setClearColor(){} setSize(w,h){this.domElement.width=w;this.domElement.height=h;this.last='';}
 setAnimationLoop(fn){const loop=()=>{fn();requestAnimationFrame(loop);};requestAnimationFrame(loop);}
 render(scene,camera){
 scene.updateMatrixWorld();camera.updateMatrixWorld();
 const signature=camera.matrixWorld.elements.join(',')+scene.children.map(o=>[o.uuid,o.visible,o.position.toArray(),o.rotation.toArray(),o.children.map(c=>[c.visible,c.position.toArray(),c.material?.opacity,c.material?.wireframe])]).flat(6).join(',');
 if(signature===this.last)return;this.last=signature;
 const c=this.context,w=this.domElement.width,h=this.domElement.height;c.fillStyle='#eef0e8';c.fillRect(0,0,w,h);
 const vp=new THREE.Matrix4().multiplyMatrices(camera.projectionMatrix,camera.matrixWorldInverse),v=new THREE.Vector3(),color=new THREE.Color();const faces=[];const dots=[];
 function project(x,y,z,m){v.set(x,y,z).applyMatrix4(m);return [(v.x+1)*w/2,(1-v.y)*h/2,v.z];}
 scene.traverseVisible(o=>{
 if(!o.geometry)return;const a=o.geometry.attributes.position;if(!a)return;const matrix=new THREE.Matrix4().multiplyMatrices(vp,o.matrixWorld),mat=o.material;
 if(o.isPoints){const colors=o.geometry.attributes.color,step=Math.max(1,Math.ceil(a.count/100000));for(let i=0;i<a.count;i+=step){const p=project(a.getX(i),a.getY(i),a.getZ(i),matrix);if(p[2]<-1||p[2]>1||p[0]<0||p[0]>w||p[1]<0||p[1]>h)continue;if(colors)color.setRGB(colors.getX(i),colors.getY(i),colors.getZ(i));else color.copy(mat.color);const rgb=color.clone().convertLinearToSRGB();dots.push({p,rgb:[rgb.r*255,rgb.g*255,rgb.b*255],size:mat.size});}return;}
 const index=o.geometry.index;const count=index?index.count:a.count;const point=i=>{const k=index?index.getX(i):i;return project(a.getX(k),a.getY(k),a.getZ(k),matrix);};
 if(o.isMesh){for(let i=0;i<count;i+=3){const pts=[point(i),point(i+1),point(i+2)];if(pts.some(p=>p[2]<-1||p[2]>1))continue;faces.push({pts,depth:pts.reduce((s,p)=>s+p[2],0)/3,color:mat.color?.getStyle()||'#c4b088',rgb:(()=>{const normal=o.geometry.attributes.normal;let light=.85;if(normal){const k=index?index.getX(i):i;const n=new THREE.Vector3(normal.getX(k),normal.getY(k),normal.getZ(k)).transformDirection(o.matrixWorld);light=.48+.52*Math.max(0,n.dot(new THREE.Vector3(-.4,-.5,.85).normalize()));}const rgb=(mat.color||new THREE.Color('#c4b088')).clone().multiplyScalar(light).convertLinearToSRGB();return [rgb.r*255,rgb.g*255,rgb.b*255];})(),opacity:mat.opacity,wire:mat.wireframe});}}
 else if(o.isLineSegments||o.isLine){c.strokeStyle=mat.color?.getStyle()||'#cad2c3';c.lineWidth=1;c.globalAlpha=mat.opacity??1;for(let i=0;i<count-1;i+=o.isLineSegments?2:1){const p=point(i),q=point(i+1);if(p[2]<-1||p[2]>1||q[2]<-1||q[2]>1)continue;c.beginPath();c.moveTo(p[0],p[1]);c.lineTo(q[0],q[1]);c.stroke();}}
 });
 const image=c.getImageData(0,0,w,h),pixels=image.data,depth=new Float32Array(w*h).fill(Infinity);
 const pixel=(x,y,z,rgb,alpha)=>{const k=y*w+x;if(z>=depth[k])return;const j=k*4;for(let ch=0;ch<3;ch++)pixels[j+ch]=rgb[ch]*alpha+pixels[j+ch]*(1-alpha);if(alpha>.95)depth[k]=z;};
 faces.sort((a,b)=>(a.opacity<.95)-(b.opacity<.95)||b.depth-a.depth);
 for(const f of faces){if(f.wire)continue;const [a,b,d]=f.pts;const area=(b[0]-a[0])*(d[1]-a[1])-(b[1]-a[1])*(d[0]-a[0]);if(Math.abs(area)<.001)continue;
 const minx=Math.max(0,Math.floor(Math.min(a[0],b[0],d[0]))),maxx=Math.min(w-1,Math.ceil(Math.max(a[0],b[0],d[0]))),miny=Math.max(0,Math.floor(Math.min(a[1],b[1],d[1]))),maxy=Math.min(h-1,Math.ceil(Math.max(a[1],b[1],d[1])));
 for(let y=miny;y<=maxy;y++)for(let x=minx;x<=maxx;x++){const u=((b[0]-x)*(d[1]-y)-(b[1]-y)*(d[0]-x))/area,v=((d[0]-x)*(a[1]-y)-(d[1]-y)*(a[0]-x))/area,t=1-u-v;if(u>=0&&v>=0&&t>=0)pixel(x,y,u*a[2]+v*b[2]+t*d[2],f.rgb,f.opacity);}}
 for(const d of dots){for(let y=Math.max(0,Math.floor(d.p[1]));y<Math.min(h,d.p[1]+d.size);y++)for(let x=Math.max(0,Math.floor(d.p[0]));x<Math.min(w,d.p[0]+d.size);x++)pixel(x,y,d.p[2],d.rgb,1);}
 c.putImageData(image,0,0);
 for(const f of faces)if(f.wire){c.strokeStyle=f.color;c.globalAlpha=f.opacity;c.beginPath();c.moveTo(...f.pts[0].slice(0,2));c.lineTo(...f.pts[1].slice(0,2));c.lineTo(...f.pts[2].slice(0,2));c.closePath();c.stroke();}c.globalAlpha=1;
 }
}
