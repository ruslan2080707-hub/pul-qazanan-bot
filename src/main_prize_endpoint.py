# Prize awarding endpoint to add to main.py

@app.route('/api/admin/award-prizes', methods=['POST'])
def award_prizes():
    """
    Начисление призов за рейтинги (только для админа)
    
    POST /api/admin/award-prizes
    Body: {
        "admin_id": 5649983054,
        "period": "daily" | "weekly" | "monthly",
        "dry_run": false
    }
    """
    try:
        data = request.json
        admin_id = data.get('admin_id')
        
        # Проверка прав админа
        if int(admin_id) != int(os.getenv('ADMIN_ID')):
            return jsonify({'error': 'Unauthorized', 'message': 'Only admin can award prizes'}), 403
        
        period = data.get('period', 'daily')
        dry_run = data.get('dry_run', False)
        
        # Валидация периода
        if period not in ['daily', 'weekly', 'monthly']:
            return jsonify({'error': 'Invalid period', 'message': 'Period must be daily, weekly, or monthly'}), 400
        
        # Импорт функции начисления призов
        from src.db_prizes import award_leaderboard_prizes
        
        # Начисление призов
        result = award_leaderboard_prizes(period, dry_run=dry_run)
        
        if result['success']:
            return jsonify({
                'success': True,
                'period': period,
                'dry_run': dry_run,
                'winners': result.get('winners', []),
                'message': f'Successfully awarded {period} prizes' if not dry_run else f'Dry run completed for {period} prizes'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error'),
                'message': result.get('message', 'Failed to award prizes')
            }), 500
            
    except Exception as e:
        logger.error(f"[PRIZES] ERROR awarding prizes: {e}")
        return jsonify({'error': str(e), 'message': 'Internal server error'}), 500

@app.route('/api/admin/prize-preview', methods=['GET'])
def prize_preview():
    """
    Предварительный просмотр победителей (без начисления)
    
    GET /api/admin/prize-preview?admin_id=5649983054&period=daily
    """
    try:
        admin_id = request.args.get('admin_id')
        
        # Проверка прав админа
        if int(admin_id) != int(os.getenv('ADMIN_ID')):
            return jsonify({'error': 'Unauthorized'}), 403
        
        period = request.args.get('period', 'daily')
        
        # Валидация периода
        if period not in ['daily', 'weekly', 'monthly']:
            return jsonify({'error': 'Invalid period'}), 400
        
        # Импорт функции
        from src.db_prizes import award_leaderboard_prizes
        
        # Dry run для предварительного просмотра
        result = award_leaderboard_prizes(period, dry_run=True)
        
        return jsonify({
            'period': period,
            'winners': result.get('winners', []),
            'prize_amounts': {
                'daily': {'1': 0.50, '2': 0.30, '3': 0.20},
                'weekly': {'1': 5.00, '2': 3.00, '3': 2.00},
                'monthly': {'1': 50.00, '2': 30.00, '3': 20.00}
            }
        })
            
    except Exception as e:
        logger.error(f"[PRIZES] ERROR in prize preview: {e}")
        return jsonify({'error': str(e)}), 500
