import os


def make_dir(directory_name):

    if not os.path.exists(directory_name):
        os.makedirs(directory_name)


def make_batch_dir(save_path, url, epoch, batch):

    directory_name = os.path.join(save_path, os.path.join(url, os.path.join(epoch, batch)))
    make_dir(directory_name)

    return directory_name


def make_sequence_dir(save_path, url, epoch):

    directory_name = os.path.join(save_path, os.path.join(url, epoch))
    make_dir(directory_name)

    return directory_name