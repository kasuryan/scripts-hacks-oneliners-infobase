allvms = c.get_all_vms(extra_attrs=True)
act_images = []
for v in allvms:
    try:
        if allvms[v].image['id'] not in act_images:
            act_images.append(allvms[v].image['id'])
    except (KeyError,TypeError) as e:
        pass
all_images_src = {i.id: i for i in c.glance.images.list() }

non_act_images_d = {}
for i in set(all_images_src.keys()) - set(act_images):
    non_act_images_d[i] = all_images_src[i]

uai_track = {}

for i in non_act_images_d:
    if 'uai' in non_act_images_d[i]:
        if non_act_images_d[i]['uai'] in uai_track:
            uai_track[non_act_images_d[i]['uai']].append(i)
        else:
            uai_track[non_act_images_d[i]['uai']] = [i]


with open('/tmp/images.txt', 'w') as f:
    for i in uai_track['UAI2008331']:
        f.write(all_images_src[i]['id'], all_images_src[i]['name'])

for i in uai_track_new['UAI2008456']['image_uuids']:
    try:
        print(non_act_images_d[i]['name'],non_act_images_d[i]['id'],non_act_images_d[i]['owner'],non_act_images_d[i]['created_at'],non_act_images_d[i]['updated_at'],non_act_images_d[i]['alternate_contacts'])
    except KeyError:
        print(non_act_images_d[i]['name'],non_act_images_d[i]['id'],non_act_images_d[i]['owner'],non_act_images_d[i]['created_at'],non_act_images_d[i]['updated_at'])

import csv

with open("/root/UAI2008456.csv", 'a') as csvfile:
    fieldnames = ['Name', 'UUID', 'Project', 'Created_at', 'Updated_at',
    'listed_contact_if_any']
    writer = csv.DictWriter(csvfile, fieldnames, dialect='excel')
    writer.writeheader()
    for i in uai_track_new['UAI2008456']['image_uuids']:
        try:
            writer.writerow({'Name':non_act_images_d[i]['name'],
            'UUID': non_act_images_d[i]['id'],
            'Project': c.keystone.projects.get(non_act_images_d[i]['owner'].name),
            'Created_at': non_act_images_d[i]['created_at'],
            'Updated_at': non_act_images_d[i]['updated_at'],
            'listed_contact_if_any': non_act_images_d[i]['alternate_contacts']})
        except KeyError:
            writer.writerow({'Name':non_act_images_d[i]['name'],
            'UUID': non_act_images_d[i]['id'],
            'Project': c.keystone.projects.get(non_act_images_d[i]['owner'].name),
            'Created_at': non_act_images_d[i]['created_at'],
            'Updated_at': non_act_images_d[i]['updated_at']})
