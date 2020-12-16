import os
from tld import get_tld


def make_dir(directory_name):

    if not os.path.exists(directory_name):
        os.makedirs(directory_name)


def make_batch_dir(save_path, url, epoch, batch):
    domain = get_domain(url)
    directory_name = os.path.join(save_path, os.path.join(domain, os.path.join(str(epoch), str(batch))))
    make_dir(directory_name)

    return directory_name


def make_sequence_dir(save_path, url, epoch):
    domain = get_domain(url)
    directory_name = os.path.join(save_path, os.path.join(domain, str(epoch)))
    make_dir(directory_name)

    return directory_name


def get_domain(url):

    result = get_tld(url, as_object=True)
    domain = result.domain
    return domain