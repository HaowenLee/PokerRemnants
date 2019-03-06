# coding=utf-8

from utils import validate_cards, format_input_cards, format_output_cards, get_rest_cards
from move_player import get_resp_moves
from minmax_engine import start_engine


class UIEngine(object):
    @staticmethod
    def declare():
        print("可输入的命令:")
        print("pass - 过，不出牌")
        print("quit - 立即退出程序")
        print("-" * 30)

    @staticmethod
    def run(lorder_cards=None, farmer_cards=None, farmer_move=None):
        if farmer_move is None:
            farmer_move = list()
        if farmer_cards is None:
            farmer_cards = list()
        if lorder_cards is None:
            lorder_cards = list()
        UIEngine.declare()

        if not lorder_cards and not farmer_cards:
            print("请输入对手的牌(以空格间隔): ")
            farmer_cards = input().split()
            while not validate_cards(farmer_cards):
                print("对手的牌输入错误，请重新输入: ")
                farmer_cards = input().split()

            print("请输入自己的牌(以空格间隔): ")
            lorder_cards = input().split()
            while not validate_cards(lorder_cards):
                print("自己的牌输入错误，请重新输入: ")
                lorder_cards = input().split()

        lorder_cards = format_input_cards(lorder_cards)
        farmer_cards = format_input_cards(farmer_cards)

        print("初始状态: ")
        print("自己家的牌: %s" % format_output_cards(lorder_cards))
        print("对手家的牌: %s" % format_output_cards(farmer_cards))
        print("当前出牌者: %s" % "自己")
        print("-" * 20)

        # LandLorder do the first move
        lorder_move = start_engine(lorder_cards=lorder_cards,
                                   farmer_cards=farmer_cards,
                                   farmer_move=farmer_move)

        if lorder_move is None:
            print("自己必败！")
            return

        lorder_cards = get_rest_cards(lorder_cards, lorder_move)
        if len(lorder_cards) == 0:
            print("自己出牌: %s" % format_output_cards(lorder_move))
            print("自己胜利!")
            return

        # Farmer and LandLorder play one by one
        while True:
            # Print the Situation after Lorder play a move
            str_lorder_move = format_output_cards(lorder_move) if lorder_move else 'Pass!'
            print("自己家的牌: %s" % format_output_cards(lorder_cards))
            print("对手家的牌: %s" % format_output_cards(farmer_cards))
            print("自己已出牌: %s" % str_lorder_move)
            print("-" * 20)

            # Farmer plays a move
            print("请帮对手出牌:")
            farmer_move = input("")
            if (farmer_move in ['pass', 'Pass', 'PASS', '不要']) or \
                    len(farmer_move.strip()) == 0:
                farmer_move = []
            elif farmer_move == 'quit':
                exit(0)
            else:
                farmer_move = format_input_cards(farmer_move.split())

            possible_moves = get_resp_moves(farmer_cards, lorder_move)
            # must sort, for 'not in' check.
            possible_moves = [sorted(move) for move in possible_moves]
            while farmer_move not in possible_moves:
                print("错误的出牌！请重新帮对手出牌: ")
                farmer_move = input("")
                if farmer_move in ['pass', 'Pass', 'PASS']:
                    farmer_move = []
                else:
                    farmer_move = format_input_cards(farmer_move.split())
                possible_moves = get_resp_moves(farmer_cards, lorder_move)
                # must sort, for 'not in' check.
                possible_moves = [sorted(move) for move in possible_moves]

            farmer_cards = get_rest_cards(farmer_cards, farmer_move)
            if len(farmer_cards) == 0:
                print("对手出牌: %s" % format_output_cards(farmer_move))
                print("对手胜利！")
                return

            str_farmer_move = format_output_cards(farmer_move) if farmer_move else 'Pass!'
            print("自己家的牌: %s" % format_output_cards(lorder_cards))
            print("对手家的牌: %s" % format_output_cards(farmer_cards))
            print("对手已出牌: %s" % str_farmer_move)
            print("-" * 20)

            # LandLorder plays a move
            lorder_move = start_engine(lorder_cards=lorder_cards, farmer_cards=farmer_cards,
                                       farmer_move=farmer_move)

            if lorder_move is None:
                print("自己必败！")
                return

            lorder_cards = get_rest_cards(lorder_cards, lorder_move)
            if len(lorder_cards) == 0:
                print("自己出牌: %s" % format_output_cards(lorder_move))
                print("自己胜利！")
                return
