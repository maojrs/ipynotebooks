import os, sys
import numpy as np
import mpld3
import glob
from clawpack.visclaw.JSAnimation import IPython_display
from matplotlib import animation
from matplotlib import image
import matplotlib.pyplot as plt
from clawpack.riemann import riemann_interactive
#from matplotlib.path import Path
import matplotlib.patches as patches
#from matplotlib.patches import Ellipse, Polygon
from IPython.html.widgets import interact
from ipywidgets import StaticInteract, RangeWidget, RadioWidget, DropDownWidget


####################################################################

#To be able to run clawpack if needed be
CLAW = os.environ.get('CLAW','/Users/rjl/git/clawpack')  
sys.path.append(CLAW)  # add to path so clawpack modules can be found
os.environ['CLAW'] = CLAW
os.environ['PYTHONPATH'] = CLAW  # so Fortran Makefiles work
example_dir = os.getcwd()
os.chdir(example_dir)

# Run shallow water solver in clawpack
def run_sw(hl=3.,ul=0.,hr=1.,ur=0.):
	os.system("make .exe")
	import setrun
	rundata = setrun.setrun()  # initialize most run-time variables for clawpack
	outdir = '_output'

	# IC for shallow water code
	rundata.probdata.hl = hl
	rundata.probdata.ul = ul
	rundata.probdata.hr = hr
	rundata.probdata.ur = ur
	rundata.write()

	os.system("make output > output.txt")
	os.system("make plots >> output.txt")


####################################################################
# For transverse solver app
# Plot diagram for transverse solver

# Set left and right state and deltaq (q = [sig11,sig22,sig12,u,v])
qL = np.array([1.0, 0.0, 0.0])
qR = np.array([0.0, 0.0, 0.0])
dq = np.array([qR[0]-qL[0], qR[1]-qL[1],qR[2]-qL[2]])

# Set normal for normal solver
nx = 1.0
ny = 0.0
# Set normal for transverse solver
nxt = 0.0
nyt = 1.0

# Set grid size (dx2=dx/2) and time step
dx2 = 0.01
dy2 = 0.01
dt = 0.01

# Set bulk and density (left and right)
bulkL = 1;   rhoL = 1 
bulkR = 8;   rhoR = 2

# Define speeds and impedance (left and right)
cL = np.sqrt(bulkL/rhoL);  ZL = rhoL*cL
cR = np.sqrt(bulkR/rhoR);  ZR = rhoR*cR

## NORMAL SOLVER

# Define the 2 eigenvectors (from columns of Matrix R)
rL = np.array([-ZL, nx, ny])
rR = np.array([ZR, nx, ny])
# Define eigenvalues
sL = -cL
sR = cR

# Compute the 2 alphas
det2 = ZL + ZR
alL = (-dq[0] + (nx*dq[1] + ny*dq[2])*ZR)/det2
alR = (dq[0] +  (nx*dq[1] + ny*dq[2])*ZL)/det2

# Compute wave fluctuations
amdq = alL*rL*sL
apdq = alR*rR*sR

## TRANSVERSE SOLVER (assuming same material on top and bottom cells)
# Define the 2 eigenvectors (from columns of Matrix R)
rB = np.array([-ZR, nxt, nyt])
rU = np.array([ZR, nxt, nyt])
# Define eigenvalues
sB = -cR
sU = cR

det2 = 2.0*ZR
beB = (-apdq[0] + (nxt*apdq[1] + nyt*apdq[2])*ZR)/det2
beU = (apdq[0] +  (nxt*apdq[1] + nyt*apdq[2])*ZR)/det2

# Compute transverse wave fluctuations
bmdq = beB*rB*sB
bpdq = beU*rU*sU

def plot_trans_diag(dt,transverse_solver_up,transverse_solver_down):
    x = np.linspace(-2*dx2,2*dx2,50);
    y1 = 0.0*x + dy2;
    y2 = 0.0*x - dy2;

    y = np.linspace(-2*dy2,2*dy2,50);
    x1 = 0.0*y + dx2;
    x2 = 0.0*y - dx2;
 
    fig = plt.figure()
    ax = fig.add_subplot(111,aspect='equal') 
    
    ax.plot(x,y1,'-k',linewidth=2)
    ax.plot(x,y2,'-k',linewidth=2)
    ax.plot(x1,y,'-k',linewidth=2)
    ax.plot(x2,y,'-k',linewidth=2)
    ax.axis([min(x),max(x),min(y),max(y)])
    ax.axis('off')
    
    xplus = sR*dt -dx2
    xminus = sL*dt -dx2
    yplus = sU*dt
    yminus = sB*dt
    
    # Main patches (A+DQ and A-DQ)
    verts = [-dx2,-dy2], [xplus,-dy2], [xplus,dy2], [-dx2,dy2] 
    poly = patches.Polygon(verts, facecolor='blue', alpha=0.35, linewidth=3) 
    ax.add_patch(poly)
    
    verts = [-dx2,-dy2], [xminus,-dy2], [xminus,dy2], [-dx2,dy2] 
    poly = patches.Polygon(verts, facecolor='blue', alpha=0.35, linewidth=3) 
    ax.add_patch(poly)
    
    #Transverse patches
    if (transverse_solver_up=='On'):
        verts = [-dx2,-dy2], [xplus,-dy2+yplus], [xplus,dy2+yplus], [-dx2,dy2] 
        poly = patches.Polygon(verts, facecolor='yellow', alpha=0.35, linewidth=3) 
        ax.add_patch(poly) 
        
    if (transverse_solver_down=='On'):
        verts = [-dx2,-dy2], [xplus,-dy2+yminus], [xplus,dy2+yminus], [-dx2,dy2] 
        poly = patches.Polygon(verts, facecolor='red', alpha=0.35, linewidth=3) 
        ax.add_patch(poly) 
    
    return fig


