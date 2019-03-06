# -*- coding: UTF-8 -*-
# Author: Tim Wu
# Author: Carl King

import operator


# 牌型枚举
class ComeType:
    PASS, SINGLE, PAIR, TRIPLE, TRIPLE_ONE, TRIPLE_TWO, FOURTH_TWO_ONES, FOURTH_TWO_PAIRS, STRAIGHT, EVEN_PAIR, BOMB = \
        range(11)


# 3-14 分别代表 3-10, J, Q, K, A
# 16, 18, 19 分别代表 2, little_joker, big_joker
# 将 2 与其他牌分开是为了方便计算顺子
# 定义 HAND_PASS 为过牌
little_joker, big_joker = 18, 19
HAND_PASS = {'type': ComeType.PASS, 'main': 0, 'component': []}


#  符号转数字
def get_val(cards):
    dicts = {'3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14,
             '2': 16, 'w': 18, 'W': 19}
    for i, card in enumerate(cards):
        cards[i] = dicts[card]


# 数字转符号
def get_card(value):
    out = value[:]
    dicts = {3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: '10', 11: 'J', 12: 'Q', 13: 'K', 14: 'A',
             16: '2', 18: 'w', 19: 'W'}
    for i, card in enumerate(value):
        out[i] = dicts[card]
    return out


# 根据当前手牌，获取此牌所有可能出的牌型
# 牌型数据结构为 {牌类型，主牌，包含的牌}
# 同种牌类型可以通过主牌比较大小
# 为方便比较大小, 将顺子按照不同长度分为不同牌型
def get_all_hands(pokers):
    if not pokers:
        return []

    # 过牌
    combs = [HAND_PASS]

    # 获取每个点数的数目
    dic = counter(pokers)

    # 王炸
    if little_joker in pokers and big_joker in pokers:
        combs.append({'type': ComeType.BOMB, 'main': big_joker, 'component': [big_joker, little_joker]})

    # 非顺子, 非王炸
    for poker in dic:
        if dic[poker] >= 1:
            # 单张
            combs.append({'type': ComeType.SINGLE, 'main': poker, 'component': [poker]})

        if dic[poker] >= 2:
            # 对子
            combs.append({'type': ComeType.PAIR, 'main': poker, 'component': [poker, poker]})

        if dic[poker] >= 3:
            # 三带零
            combs.append({'type': ComeType.TRIPLE, 'main': poker, 'component': [poker, poker, poker]})
            for poker2 in dic:
                if ALLOW_THREE_ONE and dic[poker2] >= 1 and poker2 != poker:
                    # 三带一
                    combs.append(
                        {'type': ComeType.TRIPLE_ONE, 'main': poker, 'component': [poker, poker, poker, poker2]})
                if ALLOW_THREE_TWO and dic[poker2] >= 2 and poker2 != poker:
                    # 三带二
                    combs.append({'type': ComeType.TRIPLE_TWO, 'main': poker,
                                  'component': [poker, poker, poker, poker2, poker2]})

        if dic[poker] == 4:
            # 炸弹
            combs.append({'type': ComeType.BOMB, 'main': poker, 'component': [poker, poker, poker, poker]})
            if ALLOW_FOUR_TWO:
                pairs = []
                ones = []
                for poker2 in dic:
                    if dic[poker2] == 1:
                        ones.append(poker2)
                    elif dic[poker2] == 2:
                        pairs.append(poker2)

                # 四带二单
                for i in range(len(ones)):
                    for j in range(i + 1, len(ones)):
                        combs.append({'type': ComeType.FOURTH_TWO_ONES, 'main': poker,
                                      'component': [poker, poker, poker, poker, ones[i], ones[j]]})

                # 四带二对
                for i in range(len(pairs)):
                    combs.append({'type': ComeType.FOURTH_TWO_ONES, 'main': poker,
                                  'component': [poker, poker, poker, poker, pairs[i], pairs[i]]})
                    for j in range(i + 1, len(pairs)):
                        combs.append({'type': ComeType.FOURTH_TWO_PAIRS, 'main': poker,
                                      'component': [poker, poker, poker, poker, pairs[i], pairs[i], pairs[j],
                                                    pairs[j]]})

    # 所有顺子组合
    # 以 COMB_TYPE.STRAIGHT * len(straight) 标志顺子牌型, 不同长度的顺子是不同的牌型
    for straight in create_straight(list(set(pokers)), 5):
        combs.append({'type': ComeType.STRAIGHT * len(straight), 'main': straight[0], 'component': straight})

    # 所有顺子组合
    # 以 COMB_TYPE.STRAIGHT * len(straight) 标志顺子牌型, 不同长度的顺子是不同的牌型
    for straight in create_straight(get_multi_poker(pokers, 2), 3):
        combs.append({'type': ComeType.EVEN_PAIR * len(straight), 'main': straight[0], 'component': straight})

    # 返回所有可能的出牌类型
    return combs


# 根据列表创建顺子
def create_straight(list_of_nums, min_length):
    a = sorted(list_of_nums)
    lens = len(a)
    for begin in range(0, lens):
        for end in range(begin, lens):
            if a[end] - a[begin] != end - begin:
                break
            elif end - begin >= min_length - 1:
                yield list(range(a[begin], a[end] + 1))


# 获取多个数的元素集合
def get_multi_poker(pokers, count):
    poker_list = set()
    for poker in pokers:
        if pokers.count(poker) >= count:
            poker_list.add(poker)
    return list(poker_list)


# 统计列表中每个元素的个数
def counter(pokers):
    dic = {}
    for poker in pokers:
        dic[poker] = pokers.count(poker)
    return dic


# comb1 先出，问后出的 comb2 是否能打过 comb1
# 1. 同种牌型比较 main 值, main 值大的胜
# 2. 炸弹大过其他牌型
# 3. 牌型不同, 后出为负
def can_beat(comb1, comb2):
    if not comb2 or comb2['type'] == ComeType.PASS:
        return False

    if not comb1 or comb1['type'] == ComeType.PASS:
        return True

    if comb1['type'] == comb2['type']:
        return comb2['main'] > comb1['main']
    elif comb2['type'] == ComeType.BOMB:
        return True
    else:
        return False


# 给定 pokers，求打出手牌 hand 后的牌
# 用 component 字段标志打出的牌, 可以方便地统一处理
def make_hand(pokers, c_hand):
    poker_clone = pokers[:]
    for poker in c_hand['component']:
        poker_clone.remove(poker)
    return poker_clone


# 模拟每次出牌, my_pokers 为当前我的牌, enemy_pokers 为对手的牌
# last_hand 为上一手对手出的牌, cache 用于缓存牌局与胜负关系, is_farmer 是否为农民出牌
# 该回合由 my_pokers 出牌
# 返回：是否能出完所有手牌
def hand_out(my_pokers, enemy_pokers, last_hand=None, cache=None, is_farmer=True, first_hand=False):
    # 牌局终止的边界条件
    if cache is None:
        cache = {}

    # 如果上一手为空, 则将上一手赋值为 HAND_PASS
    if last_hand is None:
        last_hand = HAND_PASS

    key = str((my_pokers, enemy_pokers, last_hand['component'], is_farmer))

    if not my_pokers:
        cache[key] = True
        return {'hand_out': True, 'cache': cache, 'tip_hand': None}

    if not enemy_pokers:
        cache[key] = False
        return {'hand_out': False, 'cache': cache, 'tip_hand': None}

    # 从缓存中读取数据
    if key in cache:
        return {'hand_out': cache[key], 'cache': cache, 'tip_hand': None}

    # 模拟出牌过程, 深度优先搜索, 找到赢的分支则返回 True
    for current_hand in get_all_hands(my_pokers):
        # 转换出牌权有两种情况:
        # 1. 当前手胜出, 则轮到对方选择出牌
        # 2. 当前手 PASS, 且对方之前没有 PASS, 则轮到对方出牌
        # 3. 如果对手出不完则，我方胜利
        if can_beat(last_hand, current_hand) or \
                (last_hand['type'] != ComeType.PASS and current_hand['type'] == ComeType.PASS):
            if not \
                    hand_out(enemy_pokers, make_hand(my_pokers, current_hand), current_hand, cache, not is_farmer)[
                        'hand_out']:
                if first_hand:
                    return {'hand_out': True, 'cache': cache, 'tip_hand': current_hand}
                else:
                    return {'hand_out': True, 'cache': cache, 'tip_hand': None}

    # 遍历所有情况, 均无法赢, 则返回 False
    cache[key] = False
    return {'hand_out': False, 'cache': cache, 'tip_hand': None}


if __name__ == '__main__':
    import time

    # 残局1
    # 是否允许三带一
    ALLOW_THREE_ONE = True
    # 是否允许三带二
    ALLOW_THREE_TWO = True
    # 是否允许四带二
    ALLOW_FOUR_TWO = True

    lord_str = input('请输入地主牌：')
    farmer_str = input('请输入农民牌：')
    lord = lord_str.split()
    farmer = farmer_str.split()

    # 使用数值代替牌面
    get_val(lord)
    get_val(farmer)

    print("正在尝试中…")

    start = time.clock()
    result = hand_out(farmer, lord, None, {}, True, True)
    # 输出结果和时间
    elapsed = (time.clock() - start)
    print("Result:", result['hand_out'])
    print("Elapsed:", elapsed)

    if result['hand_out']:

        hand_cache = result['cache']
        # 农名自动出牌
        farmer = make_hand(farmer, result['tip_hand'])
        # 提示出牌
        print("提示出牌: ", get_card(result['tip_hand']['component']))

        flag = 1
        while flag:
            # 输入地主的出牌
            # 如果是 q 重新开始
            lord_move_str = input('请输入地主的出牌：')
            if lord_move_str == 'q':
                lord_str = input('请输入地主牌：')
                farmer_str = input('请输入农民牌：')
                lord = lord_str.split()
                farmer = farmer_str.split()

                # 使用数值代替牌面
                get_val(lord)
                get_val(farmer)

                print("正在尝试中…")

                start = time.clock()
                result = hand_out(farmer, lord, None, {}, True, True)
                hand_cache = result['cache']
                # 农名自动出牌
                farmer = make_hand(farmer, result['tip_hand'])
                # 提示出牌
                print("提示出牌: ", get_card(result['tip_hand']['component']))
                # 输出结果和时间
                elapsed = (time.clock() - start)
                print("Result:", result['hand_out'])
                print("Elapsed:", elapsed)
                continue

            lord_temp = lord[:]

            # 解析地主输入的牌
            lord_move = lord_move_str.split()
            get_val(lord_move)
            for obj in lord_move:
                lord.remove(obj)

            lord_hand = None
            for hand in get_all_hands(lord_temp):
                if operator.eq(hand['component'], lord_move):
                    lord_hand = hand

            print("正在尝试中…")

            # 计算提示出牌，从遍历的缓存取
            start = time.clock()
            success = False

            # 遍历尝试
            for hand in get_all_hands(farmer):
                farmer_try = farmer[:]
                farmer_try = make_hand(farmer_try, hand)
                key_try = str((lord, farmer_try, hand['component'], False))
                if key_try in result['cache'] and not result['cache'][key_try]:
                    if can_beat(lord_hand, hand) or not hand['component']:
                        farmer = make_hand(farmer, hand)
                        success = True
                        # 提示出牌
                        print("提示出牌: ", get_card(hand['component']))
                        break
            elapsed = (time.clock() - start)
            print("Result:", success)
            print("Elapsed:", elapsed)

            # 农民出完了
            if len(farmer) == 0:
                print("出完了所有的牌了...\n")
                lord_str = input('请输入地主牌：')
                farmer_str = input('请输入农民牌：')
                lord = lord_str.split()
                farmer = farmer_str.split()

                # 使用数值代替牌面
                get_val(lord)
                get_val(farmer)

                print("正在尝试中…")

                start = time.clock()
                result = hand_out(farmer, lord, None, {}, True, True)
                hand_cache = result['cache']
                # 农名自动出牌
                farmer = make_hand(farmer, result['tip_hand'])
                # 提示出牌
                print("提示出牌: ", get_card(result['tip_hand']['component']))
                # 输出结果和时间
                elapsed = (time.clock() - start)
                print("Result:", result['hand_out'])
                print("Elapsed:", elapsed)
