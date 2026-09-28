from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
R=Path(__file__).resolve().parents[1];D=json.loads((R/'viewer/model.json').read_text())
fig=plt.figure(figsize=(13,12),facecolor='#101a22');ax=fig.add_axes([.04,.08,.80,.86],projection='3d');ax.set_facecolor('#101a22')
for inst in D['instances']:
    if not inst['visible']:continue
    mesh=D['meshes'][inst['key']];v=np.array(mesh['vertices']).reshape(-1,3);f=np.array(mesh['faces']).reshape(-1,3);m=np.array(inst['matrix']);v=v@m[:3,:3].T+m[:3,3]
    c=Poly3DCollection(v[f],facecolors=D['colors'][inst['kind']],linewidth=0,alpha=1,shade=True);ax.add_collection3d(c)
ax.set_xlim(-145,100);ax.set_ylim(-265,245);ax.set_zlim(-45,100);ax.set_box_aspect([245,510,145]);ax.view_init(elev=56,azim=-70);ax.set_axis_off()
fig.text(.06,.94,'ANATOMY TENDON HAND / '+D['parameters']['revision'],color='#eef5f7',fontsize=24,weight='bold');fig.text(.06,.905,'Proximal muscle cassette. Paired forearm rails. Articulated wrist.',color='#adc0cb',fontsize=13)
fig.text(.81,.70,'FINGER MODULES',color='#77afbb',fontsize=10,weight='bold');fig.text(.81,.675,'Pinned joints\nPalmar flexor guides\nDorsal elastic returns',color='#bfd1db',fontsize=11,linespacing=1.7,va='top')
fig.text(.81,.52,'THUMB',color='#dfac56',fontsize=10,weight='bold');fig.text(.81,.495,'Two flexion joints\nSeparate opposition axis\nTwo-axis wrist below palm',color='#bfd1db',fontsize=11,linespacing=1.7,va='top')
fig.text(.81,.36,'FOREARM',color='#dfac56',fontsize=10,weight='bold');fig.text(.81,.335,'Eight proximal motors\n16 mm spool cores\nTapered removable skin',color='#bfd1db',fontsize=11,linespacing=1.7,va='top')
fig.text(.06,.05,'DESIGN STUDY  •  Actual CAD meshes  •  Motor / horn interfaces provisional  •  No physical load validation',color='#98adb9',fontsize=10)
dest=R/'output/A1/assembly/anatomy_preview.png' if D['parameters']['revision']=='A1' else R/'output/renders/assembly.png'
fig.savefig(dest,dpi=150,facecolor=fig.get_facecolor());plt.close(fig)
print('Rendered',dest)
