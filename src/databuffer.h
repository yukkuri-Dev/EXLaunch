/**
	\file databuffer.h
	Network buffer handling routines.
	OpenOBEX library - Free implementation of the Object Exchange protocol.

	Copyright (c) 2005 Herton Ronaldo Krzesinski, All Rights Reserved.

	OpenOBEX is free software; you can redistribute it and/or modify
	it under the terms of the GNU Lesser General Public License as
	published by the Free Software Foundation; either version 2.1 of
	the License, or (at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU Lesser General Public License for more details.

	You should have received a copy of the GNU Lesser General Public
	License along with OpenOBEX. If not, see <http://www.gnu.org/>.
 */

#ifndef DATABUFFER_H
#define DATABUFFER_H

#define __need_size_t
#include <stddef.h>
#include <stdint.h>


typedef struct {
	uint8_t *buffer; // 確保されたバッファ領域を指します
	uint8_t *data; // *buffer 内で有効データがある位置を指します
	size_t head_avail; // バッファ先頭にある利用可能な領域のサイズ
	size_t data_avail; // head/tail に特定されない利用可能な領域のサイズ
	size_t tail_avail; // バッファ末尾にある利用可能な領域のサイズ
	size_t data_size; // 使用中のデータサイズ
} buf_t;

buf_t *buf_new(size_t default_size);
size_t buf_total_size(buf_t *p);
void buf_resize(buf_t *p, size_t new_size);
buf_t *buf_reuse(buf_t *p);
void *buf_reserve_begin(buf_t *p, size_t data_size);
void *buf_reserve_end(buf_t *p, size_t data_size);
void buf_insert_begin(buf_t *p, uint8_t *data, size_t data_size);
void buf_insert_end(buf_t *p, uint8_t *data, size_t data_size);
void buf_remove_begin(buf_t *p, size_t data_size);
void buf_remove_end(buf_t *p, size_t data_size);
void buf_dump(buf_t *p, const char *label);
void buf_free(buf_t *p);

#endif
