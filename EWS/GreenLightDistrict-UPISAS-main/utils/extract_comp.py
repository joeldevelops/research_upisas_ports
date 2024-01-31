import pandas as pd
import numpy as np

train_data = pd.read_csv('train_data.csv')
compositions = train_data[['Config ID', 'Config Composition']].drop_duplicates()


num_rows = len(compositions)
columns = ["ID", "Composition", "Request", "Http", "Compression", "Cache"]

comp_df = pd.DataFrame(np.zeros((num_rows, len(columns)), dtype=int), columns=columns)
comp_df["ID"] = compositions["Config ID"].values
comp_df["Composition"] = compositions["Config Composition"].values


def extract_component(string):
    parts = string.split('/')
    component = parts[-1]
    return component[:-2]

def break_comp(composition_str, common_parts):
    composition_str = composition_str[1:-1].split("|")[0]

    composition_parts = composition_str.split(",")
    composition_parts = [extract_component(part) for part in composition_parts]

    all_parts = set(composition_parts)

    if not common_parts:
        common_parts = all_parts
    else:
        common_parts = common_parts.intersection(composition_parts)

    uncommon_parts = all_parts.difference(common_parts)
    print("Uncommon parts:", len(uncommon_parts))
    print(uncommon_parts)
    print("=================")
    return common_parts, uncommon_parts


cache_dict = {
    "LFU": 2,
    "LRU": 3,
    "MRU": 4,
    "RR": 5,
    "FS": 6,
}

http_dict = {
    "GETCHCMP": 2,
    "GETCH": 3,
    "GETCMP": 4,
}

def categorize_component(id, component):
    if "RequestHandler" in component:
        comp_df.at[id, "Request"] = 1
        if "PT" in component:
            comp_df.at[id, "Request"] = 2
    elif "CacheHandler" in component:
        comp_df.at[id, "Cache"] = 1
        for cache in cache_dict:
            if cache in component:
                comp_df.at[id, "Cache"] = cache_dict[cache]
                break
    elif "HTTP" in component:
        comp_df.at[id, "Http"] = 1
        for http in http_dict:
            if http in component:
                comp_df.at[id, "Http"] = http_dict[http]
                break
    elif "GZ" in component:
        comp_df.at[id, "Compression"] = 1
    elif "ZLIB" in component:
        comp_df.at[id, "Compression"] = 2


common_parts = set()

for comp in comp_df.itertuples():
    common_parts, uncommon_parts = break_comp(comp.Composition, common_parts)
    for part in uncommon_parts:
        categorize_component(comp.ID, part)


print("Common parts:", common_parts)
print("=====================")

comp_df.to_csv("compositions.csv", index=False)

comp_df = comp_df.drop('Composition', axis=1)
comp_df = comp_df.rename(columns={'ID': 'Config ID'})

print(comp_df)

# Left join on different columns
result_df = pd.merge(train_data, comp_df, on='Config ID', how='left')


print(result_df)

result_df.to_csv("train_data_with_comp.csv", index=False)