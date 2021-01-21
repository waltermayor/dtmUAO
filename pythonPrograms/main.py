#!/usr/bin/python
#! -*- encoding: utf-8 -*-

import os
import subprocess
import sys
import shutil
os.chdir("../")
PATH_TO_PROJECT=os.getcwd()
SFM_PYTHON_WRAPPER= os.path.join(PATH_TO_PROJECT,'3dparty/openMVG_Build/software/SfM/')
sys.path.append(SFM_PYTHON_WRAPPER)
import SfM_SequentialPipeline

class aerial3DMapTools():

	def __init__(self):

		print ("0. setting paths")

		self.PATH_TO_PROJECT=os.getcwd()
		self.PATH_TO_3LIBRARIES=self.PATH_TO_PROJECT+"/3dparty/"
		self.OPENMVG_SFM_BIN = self.PATH_TO_3LIBRARIES +"openMVG_Build/Linux-x86_64-RELEASE"
		self.CMVS_PMVS_BIN = self.PATH_TO_3LIBRARIES +"CMVS_PMVS"
		self.MVS_BIN= self.PATH_TO_3LIBRARIES + "openMVS_build/bin"
		self.POTREECONVERTER_BIN=self.PATH_TO_3LIBRARIES +"/PotreeConverter/master/PotreeConverter"

		self.new_project="aukerman"
		#focus="7072.43"
		self.focus="3625.47"
		self.input_dir=os.path.join(self.PATH_TO_PROJECT+"/imageInput",self.new_project)
		#output_dir=os.path.join(PATH_TO_PROJECT+"/output",new_project)
		self.output_dir=self.input_dir+"/reconstruction"
		self.reconstruction_dir = os.path.join(self.output_dir, "reconstruction_sequential")
		self.matches_dir = os.path.join(self.output_dir, "matches")
		self.PMVS_dir = self.output_dir


	def sequential_SFM(self):

		print ("1. Compute SFM Sequential")
		sfmSeq=SfM_SequentialPipeline.SfM_Sequential(self.input_dir,self.output_dir,self.focus)
		sfmSeq.pipelineSequential()

	def dense_PMVS(self):

		print ("2. Compute Dense pointCloud PMVS")
		#shutil.copy2(matches_dir+"/sfm_data.json", PATH_TO_PROJECT+"/sfm_data.json")
		pMVG2PMVS = subprocess.Popen([os.path.join(self.OPENMVG_SFM_BIN,
						"openMVG_main_openMVG2PMVS"),"-i",
						self.reconstruction_dir+"/sfm_data.bin","-o",self.PMVS_dir])
		pMVG2PMVS.wait()
		pDensePMVS=subprocess.Popen([os.path.join(self.CMVS_PMVS_BIN,"pmvs2"),
						self.PMVS_dir+"/PMVS/","pmvs_options.txt"])
		pDensePMVS.wait()

	def dense_CMVS(self):

		print ("2. Compute Dense pointCloud CMVS")

	def dense_MVS(self):

		print ("2. Compute Dense pointCloud MVS")

		if not os.path.exists(self.output_dir+"/MVS"):
		  	os.mkdir(self.output_dir+"/MVS")

		if not os.path.exists(self.output_dir+"/MVS/outputDense"):
		  	os.mkdir(self.output_dir+"/MVS/outputDense")

		pMVG2MVS = subprocess.Popen([os.path.join(self.OPENMVG_SFM_BIN,"openMVG_main_openMVG2openMVS"),
						"-i", self.reconstruction_dir+"/sfm_data.bin",
						"-o",self.output_dir+"/MVS/scene.mvs","-d",
						self.output_dir+"/MVS/undistortedImages/"])
		pMVG2MVS.wait()

		#subprocess.call('cd '+self.output_dir+' && mkdir MVS &&' 
		#+self.OPENMVG_SFM_BIN+'./openMVG_main_openMVG2openMVS -i 
		#'+self.output_dir+'/OpenMVG/reconstruction_sequential/sfm_data.bin -o 
		#'+self.output_dir+'/MVS/scene.mvs', shell=True)
		

		os.chdir(self.output_dir+"/MVS/outputDense")
		pDenseMVS=subprocess.Popen([os.path.join(self.MVS_BIN,"DensifyPointCloud"),self.output_dir+"/MVS/scene.mvs"])
		pDenseMVS.wait()
		os.chdir(self.PATH_TO_PROJECT)
		

	def mesh_MVS(self):
		
		print ("3. Compute mesh pointCloud MVS")
		
		if not os.path.exists(self.output_dir+"/MVS/meshLogs"):
		  	os.mkdir(self.output_dir+"/MVS/meshLogs")

		os.chdir(self.output_dir+"/MVS/meshLogs")
		inputFile=self.output_dir+"/MVS/scene_dense.mvs"
		pMeshMVS=subprocess.Popen([os.path.join(self.MVS_BIN,"ReconstructMesh"),inputFile])
		pMeshMVS.wait()
		os.chdir(self.PATH_TO_PROJECT)

	def refineMesh_MVS(self):
		
		print ("4. Compute refine mesh MVS")

		if not os.path.exists(self.output_dir+"/MVS/refineLogs"):
		  	os.mkdir(self.output_dir+"/MVS/refineLogs")

		os.chdir(self.output_dir+"/MVS/refineLogs")

		inputFile=self.output_dir+"/MVS/scene_mesh.mvs"
		pRefineMVS=subprocess.Popen([os.path.join(self.MVS_BIN,"RefineMesh"),inputFile])
		pRefineMVS.wait()
		os.chdir(self.PATH_TO_PROJECT)

	def textureMesh_MVS(self):

		print ("5. Compute texture mesh MVS")
		if not os.path.exists(self.output_dir+"/MVS/textureLogs"):
		  	os.mkdir(self.output_dir+"/MVS/textureLogs")

		os.chdir(self.output_dir+"/MVS/textureLogs")
		inputFile=self.output_dir+"/MVS/scene_dense_mesh.mvs"
		pRefineMVS=subprocess.Popen([os.path.join(self.MVS_BIN,"TextureMesh"),inputFile])
		pRefineMVS.wait()
		
		os.chdir(self.PATH_TO_PROJECT)

	def viewPotree_PoinClouds(self):
		print ("6 visualize pointCloud Potree")
		inputFile=self.output_dir+"/MVS/scene_dense.ply"
		namePage="mapa"
		pRefineMVS=subprocess.Popen(["sudo", os.path.join(self.POTREECONVERTER_BIN,"PotreeConverter"),"-i",inputFile,
						"-o","/var/www/html/potree","--generate-page",namePage])
		pRefineMVS.wait()
		
		


				
 
if __name__ == "__main__":

	map3d=aerial3DMapTools()
	#map3d.sequential_SFM()
	#map3d.dense_PMVS()
	#map3d.dense_MVS()
	map3d.mesh_MVS()
	map3d.refineMesh_MVS()
	map3d.textureMesh_MVS()
	#map3d.viewPotree_PoinClouds()



