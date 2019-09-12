import pandas as pd
from collections import defaultdict
import random
import matplotlib.pyplot as plt
import fnmatch
import os
import wget
import subprocess
import pkg_resources

METADATA_PATH = pkg_resources.resource_filename('cpimgs', 'data/metadata')
CPD_NAME2BRD_ID_PATH = pkg_resources.resource_filename('cpimgs', 'data/CPD_name2BRD_ID.csv')

def getVersion():
    return "0.1.0"

def getDMSO(plate, well=None):
    '''
    @plate: the plate search for DMSO
    @well: use for find the well close to
    return: a well number i.e. "o05", which is the nearest DMSO well
    '''
    df_brd2Plate_well = pd.read_csv(METADATA_PATH, sep=" ")
    df_dmso = df_brd2Plate_well[pd.isnull(df_brd2Plate_well["Metadata_pert_id"])]
    # todo: find nearst dmso
    rand_num = random.randint(0, df_dmso[df_dmso["Metadata_Plate"] == plate].shape[0])
    well_dmso = df_dmso[df_dmso["Metadata_Plate"] == plate].iloc[rand_num]["Metadata_Well"]
    print(f"Looking at DMSO from well {well_dmso}")
    return well_dmso

def getAllDMSO(plate, well=None):
    '''
    @plate: the plate search for DMSO
    @well: use for find the well close to
    return: all well numbers i.e. ["o05", "k27"]
    '''
    df_brd2Plate_well = pd.read_csv(METADATA_PATH, sep=" ")
    df_dmso = df_brd2Plate_well[pd.isnull(df_brd2Plate_well["Metadata_pert_id"])]
    # todo: find nearst dmso
    return df_dmso[df_dmso["Metadata_Plate"] == plate]["Metadata_Well"]

def getPlateWellByCpdName(name):
    '''arg: compound name or brd id
        output: {plate : wells}
    '''
    print("we are in package version 0.09")
    df_brd2Plate_well = pd.read_csv(METADATA_PATH, sep=" ")
    df_brd2Plate_well.dropna(inplace=True)
    df_name2id = pd.read_csv(CPD_NAME2BRD_ID_PATH, index_col="CPD_NAME")

    if not name.startswith("BRD"):
        try:
            brd_id = df_name2id.loc[name]["BROAD_ID"]
        #         print(brd_id)
        except:
            raise KeyError(f"{name} not found")
    else:
        brd_id = name

    df_plate_well = df_brd2Plate_well[df_brd2Plate_well["Metadata_pert_id"] == brd_id]
    res = defaultdict(list)
    for index, row in df_plate_well.iterrows():
        res[row["Metadata_Plate"]].append(row["Metadata_Well"])
    return res


def getImgsByPltWelChn(d, channel, verbose=True, save_to="tmp.png", samples_shown=1):
    '''
    @d: res from getPlateWellByCpdName the plates and wells dict corresponding to the specific chemical
    '''

    CHANNELS = ["Hoechst", 'ERSyto', 'ERSytoBleed', 'Ph_golgi', 'Mito']

    def getImgs(well, title="None"):
        subprocess.call(["unzip", "-a", f"{plate}-{channel}.zip", f"*_{well}_s*"])
        imgs = []
        for f in os.listdir(f'./{folder}'):
            if fnmatch.fnmatch(f, f'*{well}_s*'):
                img = plt.imread(f"{folder}/{f}")
                imgs.append(img)
        return imgs

    def show(imgs1, imgs2):
        fig, axes = plt.subplots(3, 4, figsize=(20, 10))

        for index in range(6):
            axes[index % 3, int(index / 3)].imshow(imgs1[index], cmap="gray")
            axes[index % 3, int(index / 3)].set_xlabel("DMSO")

        for index in range(6, 12):
            i = index - 6
            axes[index % 3, int(index / 3)].imshow(imgs2[i], cmap="gray")
            axes[index % 3, int(index / 3)].set_xlabel("Drug")
        fig.suptitle("DMSO vs drug")
        plt.savefig(save_to)
        plt.show()
        plt.clf()

    def getFolder():
        folder = ""
        for f in os.listdir('.'):
            if fnmatch.fnmatch(f, f'{plate}-{channel}'):
                return f
        return folder

    def getFolderZip():
        folderZip = ""
        for f in os.listdir('.'):
            if fnmatch.fnmatch(f, f'{plate}-{channel}.zip'):
                return f
        return folderZip

    sample_index = 0
    for plate in d:
        if verbose:
            print(f"Looking for plate {plate} in channel {channel} at folder {os.getcwd()}")

        folder = getFolder()
        folderZip = getFolderZip()

        if folder == "" and folderZip == "":
            folder = f'{plate}-{channel}'
            url = f"http://ccdb-portal.crbs.ucsd.edu/broad_data/plate_{plate}/{plate}-{channel}.zip"
            if verbose:
                print(f"Downloading plate {plate} channel {channel} datafrom ccdb-portal with {url}")

            try:
                filename = wget.download(url)
                if verbose:
                    print(f"Downloading done.")
            except:
                raise ValueError(
                    f"Can't download file for the specified the plate and channel, check the channel list {CHANNELS}")

        for well in d[plate]:
            print(f"Looking at well {well}")
            show(getImgs(getDMSO(plate, well), "DMSO"), getImgs(well, "Drug"))
        # todo: remove the break below will download all the plate data
        sample_index += 1
        if sample_index == samples_shown:
            break

def getPlotsByNameAndChn(Cpn_name, channel, samples_shown=1):
    """
    :param Cpn_name: compound name or brd id
    :param channel: one of the 5 channels people use to see cells ["Hoechst", 'ERSyto', 'ERSytoBleed', 'Ph_golgi', 'Mito']
    :param samples_shown: number of samples shown, most time will just take a look at one sample
    :return:
    """
    getImgsByPltWelChn(getPlateWellByCpdName(Cpn_name), channel=channel, samples_shown=samples_shown)


