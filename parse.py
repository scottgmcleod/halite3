import json
import os
import zstd

import pandas as pd
import hlt

ARBITRARY_ID = -1


def parse_replay_file(file):
    with open(file, 'rb') as f:
        return json.loads(zstd.loads(f.read()))


def parse_replay_folder(folder, max_files=None):
    replay_buffer = []
    for file_name in sorted(os.listdir(folder)):
        if not file_name.endswith(".hlt"):
            continue
        elif max_files is not None and len(replay_buffer) >= max_files:
            break
        else:
            replay_buffer.append(parse_replay_file(os.path.join(folder, file_name)))
    return replay_buffer


def evaluate_file(file):
    result = []
    data = parse_replay_file(file)
    for player in data['game_statistics']['player_statistics']:
        result.append(player['final_production'])
    return result


def evaluate_folder(folder):
    result = []
    for file_name in sorted(os.listdir(folder)):
        if not file_name.endswith(".hlt"):
            continue
        else:
            result.append(evaluate_file(os.path.join(folder, file_name)))
    df = pd.DataFrame(result)
    return df.divide(df.max(axis=1), axis=0).mean()
    

if __name__ == '__main__':
    parse_replay_file(
        file=r'replays/'
             r'calibrator_p4_s32_d20181222_t112808/'
             r'i0_earlygame/'
             r'replay-20181201-145702+0600-1543654521-32-32.hlt')
    parse_replay_folder(
        folder=r'replays/'
               r'calibrator_p4_s32_d20181222_t112808/'
               r'i0_earlygame')